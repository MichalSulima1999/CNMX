// IPC Server - Named Pipe Communication

#include "cnmod_hook.h"
#include "ipc/pipe_server.h"
#include "ipc/protocol.h"
#include "registry/job_registry.h"
#include "registry/production_registry.h"
#include "registry/good_registry.h"
#include "registry/ui_registry.h"
#include "utils/logging.h"

#include <windows.h>
#include <thread>
#include <mutex>
#include <atomic>
#include <condition_variable>

namespace CNMod {

namespace {

HANDLE g_pipe_handle = INVALID_HANDLE_VALUE;
std::thread g_pipe_thread;
std::atomic<bool> g_pipe_running{false};

constexpr size_t PIPE_BUFFER_SIZE = 8192;
constexpr DWORD PIPE_TIMEOUT = 5000;

// ============================================================================
// Request Processing
// ============================================================================

std::string CreateErrorResponse(uint32_t request_id, int32_t error_code, const char* message) {
    std::ostringstream oss;
    oss << "{\"request_id\":" << request_id << ",\"result\":" << error_code << ",\"error\":\"" << message << "\"}";
    return oss.str();
}

std::string CreateSuccessResponse(uint32_t request_id, const std::string& payload = "") {
    std::ostringstream oss;
    oss << "{\"request_id\":" << request_id << ",\"result\":0";
    if (!payload.empty()) oss << ",\"payload\":" << payload;
    oss << "}";
    return oss.str();
}

std::string ProcessRegisterJob(const rapidjson::Document& doc) {
    JobDefinition job;
    job.job_id = doc["job_id"].GetUint();
    if (doc.HasMember("name")) strncpy(job.name, doc["name"].GetString(), sizeof(job.name)-1);
    if (doc.HasMember("description")) strncpy(job.description, doc["description"].GetString(), sizeof(job.description)-1);
    if (doc.HasMember("building_type")) job.building_type = doc["building_type"].GetUint();
    if (doc.HasMember("output_good")) job.output_good = doc["output_good"].GetUint();
    if (doc.HasMember("input_goods") && doc["input_goods"].IsArray()) {
        const auto& arr = doc["input_goods"];
        for (size_t i = 0; i < arr.Size() && i < 8; ++i) job.input_goods[i] = arr[i].GetUint();
    }
    if (doc.HasMember("input_counts") && doc["input_counts"].IsArray()) {
        const auto& arr = doc["input_counts"];
        for (size_t i = 0; i < arr.Size() && i < 8; ++i) job.input_counts[i] = arr[i].GetUint();
    }
    if (doc.HasMember("worker_count")) job.worker_count = doc["worker_count"].GetUint();
    if (doc.HasMember("flags")) job.flags = doc["flags"].GetUint();
    
    bool ok = JobRegistry::Instance().RegisterJob(job);
    return ok ? CreateSuccessResponse(0, "\"Job registered\"") : CreateErrorResponse(0, -1, "Failed to register job");
}

std::string ProcessRegisterProduction(const rapidjson::Document& doc) {
    ProductionChain chain;
    chain.building_type = doc["building_type"].GetUint();
    chain.output_good = doc["output_good"].GetUint();
    if (doc.HasMember("input_goods") && doc["input_goods"].IsArray()) {
        const auto& arr = doc["input_goods"];
        for (size_t i = 0; i < arr.Size() && i < 8; ++i) chain.input_goods[i] = arr[i].GetUint();
    }
    if (doc.HasMember("input_counts") && doc["input_counts"].IsArray()) {
        const auto& arr = doc["input_counts"];
        for (size_t i = 0; i < arr.Size() && i < 8; ++i) chain.input_counts[i] = arr[i].GetUint();
    }
    if (doc.HasMember("production_time")) chain.production_time = doc["production_time"].GetUint();
    if (doc.HasMember("worker_job")) chain.worker_job = doc["worker_job"].GetUint();
    if (doc.HasMember("max_workers")) chain.max_workers = doc["max_workers"].GetUint();
    if (doc.HasMember("requires_building_completion")) chain.requires_building_completion = doc["requires_building_completion"].GetBool();
    
    bool ok = ProductionRegistry::Instance().RegisterProduction(chain);
    return ok ? CreateSuccessResponse(0, "\"Production registered\"") : CreateErrorResponse(0, -1, "Failed to register production");
}

std::string ProcessRegisterGood(const rapidjson::Document& doc) {
    GoodDefinition good;
    good.good_id = doc["good_id"].GetUint();
    good.type = doc.HasMember("type") ? doc["type"].GetUint() : 0;
    if (doc.HasMember("name")) strncpy(good.name, doc["name"].GetString(), sizeof(good.name)-1);
    if (doc.HasMember("description")) strncpy(good.description, doc["description"].GetString(), sizeof(good.description)-1);
    if (doc.HasMember("landscapetype")) good.landscapetype = doc["landscapetype"].GetUint();
    if (doc.HasMember("isInputGoodFlag")) good.is_input = doc["isInputGoodFlag"].GetBool();
    if (doc.HasMember("isProducedInHouseFlag")) good.is_produced_in_house = doc["isProducedInHouseFlag"].GetBool();
    if (doc.HasMember("isProducedOnMapFlag")) good.is_produced_on_map = doc["isProducedOnMapFlag"].GetBool();
    if (doc.HasMember("atomicForProduction")) good.atomic_for_production = doc["atomicForProduction"].GetUint();
    if (doc.HasMember("isBioLandscapeFlag")) good.is_bio_landscape = doc["isBioLandscapeFlag"].GetBool();
    
    bool ok = GoodRegistry::Instance().RegisterGood(good);
    return ok ? CreateSuccessResponse(0, "\"Good registered\"") : CreateErrorResponse(0, -1, "Failed to register good");
}

std::string ProcessRegisterUIStrings(const rapidjson::Document& doc) {
    UIStrings ui;
    ui.job_id = doc["job_id"].GetUint();
    if (doc.HasMember("ui_name")) strncpy(ui.ui_name, doc["ui_name"].GetString(), sizeof(ui.ui_name)-1);
    if (doc.HasMember("ui_description")) strncpy(ui.ui_description, doc["ui_description"].GetString(), sizeof(ui.ui_description)-1);
    if (doc.HasMember("ui_icon")) strncpy(ui.ui_icon, doc["ui_icon"].GetString(), sizeof(ui.ui_icon)-1);
    
    bool ok = UIRegistry::Instance().RegisterUIStrings(ui);
    return ok ? CreateSuccessResponse(0, "\"UI strings registered\"") : CreateErrorResponse(0, -1, "Failed to register UI strings");
}

std::string ProcessHotReload() {
    CNMod::RequestHotReload();
    return CreateSuccessResponse(0, "\"Hot reload requested\"");
}

std::string ProcessGetStatus() {
    std::ostringstream oss;
    oss << "{\"hooks_installed\":" << CNMod::g_hooks_installed.load()
        << ",\"jobs\":" << JobRegistry::Instance().GetAllJobIds().size()
        << ",\"productions\":" << ProductionRegistry::Instance().GetAllBuildingTypes().size()
        << ",\"goods\":" << GoodRegistry::Instance().GetAllGoodIds().size()
        << "}";
    return CreateSuccessResponse(0, oss.str());
}

std::string ProcessGetJobList() {
    std::ostringstream oss;
    oss << "[";
    auto jobs = JobRegistry::Instance().GetAllJobIds();
    for (size_t i = 0; i < jobs.size(); ++i) {
        if (i > 0) oss << ",";
        auto* job = JobRegistry::Instance().GetJob(jobs[i]);
        if (job) {
            oss << "{\"job_id\":" << jobs[i] << ",\"name\":\"" << job->name << "\",\"building\":" << job->building_type << ",\"output\":" << job->output_good << "}";
        }
    }
    oss << "]";
    return CreateSuccessResponse(0, oss.str());
}

// ============================================================================
// Main Request Processor
// ============================================================================

IPCResponse ProcessIPCRequest(const IPCRequest& req) {
    IPCResponse resp;
    resp.request_id = req.request_id;
    
    try {
        rapidjson::Document doc;
        if (req.payload_size > 0) {
            doc.Parse(reinterpret_cast<const char*>(req.payload + sizeof(IPCRequest)));
            if (doc.HasParseError()) {
                resp.result = -2;
                return resp;
            }
        }
        
        std::string payload;
        
        switch (static_cast<IPCCommand>(req.command)) {
            case IPCCommand::REGISTER_JOB:
                payload = ProcessRegisterJob(doc);
                break;
            case IPCCommand::REGISTER_PRODUCTION:
                payload = ProcessRegisterProduction(doc);
                break;
            case IPCCommand::REGISTER_GOOD:
                payload = ProcessRegisterGood(doc);
                break;
            case IPCCommand::REGISTER_UI_STRINGS:
                payload = ProcessRegisterUIStrings(doc);
                break;
            case IPCCommand::HOT_RELOAD:
                payload = ProcessHotReload();
                break;
            case IPCCommand::GET_STATUS:
                payload = ProcessGetStatus();
                break;
            case IPCCommand::GET_JOB_LIST:
                payload = ProcessGetJobList();
                break;
            default:
                resp.result = -3;
                return resp;
        }
        
        resp.result = 0;
        resp.payload_size = static_cast<uint32_t>(payload.size());
        resp.payload = std::make_unique<uint8_t[]>(payload.size());
        memcpy(resp.payload.get(), payload.data(), payload.size());
        
    } catch (const std::exception& e) {
        resp.result = -10;
        std::string err = "Exception: " + std::string(e.what());
        resp.payload_size = static_cast<uint32_t>(err.size());
        resp.payload = std::make_unique<uint8_t[]>(resp.payload_size);
        memcpy(resp.payload.get(), err.data(), resp.payload_size);
    }
    
    return resp;
}

// ============================================================================
// Pipe Server Thread
// ============================================================================

static void PipeServerThread() {
    LOG_INFO("Pipe server thread started");
    
    while (g_pipe_running.load()) {
        g_pipe_handle = CreateNamedPipeW(
            L"\\\\.\\pipe\\CNMod_ModdingAPI",
            PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED,
            PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
            PIPE_UNLIMITED_INSTANCES,
            PIPE_BUFFER_SIZE, PIPE_BUFFER_SIZE,
            PIPE_TIMEOUT,
            nullptr
        );
        
        if (g_pipe_handle == INVALID_HANDLE_VALUE) {
            LOG_ERROR("CreateNamedPipe failed: %lu", GetLastError());
            Sleep(1000);
            continue;
        }
        
        LOG_DEBUG("Waiting for client connection...");
        BOOL connected = ConnectNamedPipe(g_pipe_handle, nullptr);
        if (!connected) {
            DWORD err = GetLastError();
            if (err == ERROR_PIPE_CONNECTED) {
                // OK
            } else if (err != ERROR_IO_PENDING) {
                LOG_ERROR("ConnectNamedPipe failed: %lu", err);
                CloseHandle(g_pipe_handle);
                g_pipe_handle = INVALID_HANDLE_VALUE;
                Sleep(100);
                continue;
            }
        }
        
        if (g_pipe_handle != INVALID_HANDLE_VALUE) {
            // Handle client (simple read/write)
            BYTE buffer[PIPE_BUFFER_SIZE];
            DWORD bytes_read = 0;
            if (ReadFile(g_pipe_handle, buffer, sizeof(buffer), &bytes_read, nullptr)) {
                if (bytes_read >= sizeof(IPCRequest)) {
                    const IPCRequest* req = reinterpret_cast<const IPCRequest*>(buffer);
                    IPCResponse resp = ProcessIPCRequest(*req);
                    
                    size_t resp_size = sizeof(IPCResponse) + resp.payload_size;
                    std::vector<BYTE> resp_buffer(resp_size);
                    memcpy(resp_buffer.data(), &resp, sizeof(IPCResponse));
                    if (resp.payload_size > 0 && resp.payload) {
                        memcpy(resp_buffer.data() + sizeof(IPCResponse), resp.payload.get(), resp.payload_size);
                    }
                    
                    DWORD bytes_written = 0;
                    WriteFile(g_pipe_handle, resp_buffer.data(), static_cast<DWORD>(resp_size), &bytes_written, nullptr);
                }
            }
            DisconnectNamedPipe(g_pipe_handle);
            CloseHandle(g_pipe_handle);
            g_pipe_handle = INVALID_HANDLE_VALUE;
        }
    }
    LOG_INFO("Pipe server thread exited");
}

} // anonymous namespace

bool StartIPCServer() {
    if (g_pipe_running.exchange(true)) return true;
    g_pipe_thread = std::thread(PipeServerThread);
    LOG_INFO("IPC server started on pipe: CNMod_ModdingAPI");
    return true;
}

bool StopIPCServer() {
    if (!g_pipe_running.exchange(false)) return true;
    if (g_pipe_handle != INVALID_HANDLE_VALUE) CancelIoEx(g_pipe_handle, nullptr);
    if (g_pipe_thread.joinable()) g_pipe_thread.join();
    LOG_INFO("IPC server stopped");
    return true;
}

} // namespace CNMod