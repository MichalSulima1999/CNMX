// Protocol Implementation

#include "cnmod_hook.h"
#include "ipc/protocol.h"
#include "utils/logging.h"
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>
#include <sstream>

namespace CNMod {

std::string CreateErrorResponse(uint32_t request_id, int32_t error_code, const char* message) {
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    writer.StartObject();
    writer.Key("request_id"); writer.Uint(request_id);
    writer.Key("result"); writer.Int(error_code);
    writer.Key("error"); writer.String(message);
    writer.EndObject();
    return sb.GetString();
}

std::string CreateSuccessResponse(uint32_t request_id, const std::string& payload) {
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    writer.StartObject();
    writer.Key("request_id"); writer.Uint(request_id);
    writer.Key("result"); writer.Int(0);
    if (!payload.empty()) {
        writer.Key("payload");
        writer.RawValue(payload.c_str(), payload.size(), rapidjson::kObjectType);
    }
    writer.EndObject();
    return sb.GetString();
}

std::string CreateJobListPayload() {
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    writer.StartArray();
    auto jobs = JobRegistry::Instance().GetAllJobIds();
    for (uint32_t job_id : jobs) {
        auto* job = JobRegistry::Instance().GetJob(job_id);
        if (!job) continue;
        writer.StartObject();
        writer.Key("job_id"); writer.Uint(job_id);
        writer.Key("name"); writer.String(job->name);
        writer.Key("building_type"); writer.Uint(job->building_type);
        writer.Key("output_good"); writer.Uint(job->output_good);
        writer.Key("worker_count"); writer.Uint(job->worker_count);
        writer.Key("flags"); writer.Uint(job->flags);
        writer.EndObject();
    }
    writer.EndArray();
    return sb.GetString();
}

std::string CreateProductionListPayload() {
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    writer.StartArray();
    auto types = ProductionRegistry::Instance().GetAllBuildingTypes();
    for (uint32_t bt : types) {
        auto* chain = ProductionRegistry::Instance().GetProduction(bt);
        if (!chain) continue;
        writer.StartObject();
        writer.Key("building_type"); writer.Uint(bt);
        writer.Key("output_good"); writer.Uint(chain->output_good);
        writer.Key("production_time"); writer.Uint(chain->production_time);
        writer.Key("worker_job"); writer.Uint(chain->worker_job);
        writer.Key("max_workers"); writer.Uint(chain->max_workers);
        writer.Key("requires_completion"); writer.Bool(chain->requires_building_completion);
        writer.Key("input_goods"); writer.StartArray();
        for (size_t i = 0; i < 8; ++i) {
            if (chain->input_goods[i] > 0) {
                writer.StartObject();
                writer.Key("good_id"); writer.Uint(chain->input_goods[i]);
                writer.Key("count"); writer.Uint(chain->input_counts[i]);
                writer.EndObject();
            }
        }
        writer.EndArray();
        writer.EndObject();
    }
    writer.EndArray();
    return sb.GetString();
}

std::string CreateGoodListPayload() {
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    writer.StartArray();
    auto goods = GoodRegistry::Instance().GetAllGoodIds();
    for (uint32_t gid : goods) {
        auto* good = GoodRegistry::Instance().GetGood(gid);
        if (!good) continue;
        writer.StartObject();
        writer.Key("good_id"); writer.Uint(gid);
        writer.Key("name"); writer.String(good->name);
        writer.Key("type"); writer.Uint(good->type);
        writer.Key("is_input"); writer.Bool(good->is_input);
        writer.Key("is_produced_in_house"); writer.Bool(good->is_produced_in_house);
        writer.Key("is_produced_on_map"); writer.Bool(good->is_produced_on_map);
        writer.Key("atomic_for_production"); writer.Uint(good->atomic_for_production);
        writer.EndObject();
    }
    writer.EndArray();
    return sb.GetString();
}

std::string CreateStatusPayload() {
    rapidjson::StringBuffer sb;
    rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
    writer.StartObject();
    writer.Key("hooks_installed"); writer.Bool(g_hooks_installed.load());
    writer.Key("jobs_count"); writer.Uint(JobRegistry::Instance().GetAllJobIds().size());
    writer.Key("productions_count"); writer.Uint(ProductionRegistry::Instance().GetAllBuildingTypes().size());
    writer.Key("goods_count"); writer.Uint(GoodRegistry::Instance().GetAllGoodIds().size());
    writer.Key("hot_reload_pending"); writer.Bool(g_hot_reload_requested.load());
    writer.EndObject();
    return sb.GetString();
}

} // namespace CNMod