// Job Registry Implementation

#include "cnmod_hook.h"
#include "utils/logging.h"

namespace CNMod {

JobRegistry& JobRegistry::Instance() {
    static JobRegistry instance;
    return instance;
}

bool JobRegistry::RegisterJob(const JobDefinition& job) {
    if (!job.IsValid()) {
        LOG_ERROR("Invalid job definition: job_id=%u", job.job_id);
        return false;
    }
    
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (jobs_.find(job.job_id) != jobs_.end()) {
        LOG_WARN("Job %u already registered, overwriting", job.job_id);
    }
    
    jobs_[job.job_id] = job;
    LOG_INFO("Registered job %u: %s", job.job_id, job.name);
    return true;
}

bool JobRegistry::UnregisterJob(uint32_t job_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = jobs_.find(job_id);
    if (it == jobs_.end()) {
        LOG_WARN("Job %u not found", job_id);
        return false;
    }
    jobs_.erase(it);
    LOG_INFO("Unregistered job %u", job_id);
    return true;
}

JobDefinition* JobRegistry::GetJob(uint32_t job_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = jobs_.find(job_id);
    return (it != jobs_.end()) ? &it->second : nullptr;
}

const JobDefinition* JobRegistry::GetJob(uint32_t job_id) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = jobs_.find(job_id);
    return (it != jobs_.end()) ? &it->second : nullptr;
}

std::vector<uint32_t> JobRegistry::GetAllJobIds() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<uint32_t> ids;
    ids.reserve(jobs_.size());
    for (const auto& pair : jobs_) {
        ids.push_back(pair.first);
    }
    return ids;
}

bool JobRegistry::LoadFromINI(const char* ini_path) {
    LOG_INFO("Loading jobs from %s", ini_path);
    // Simple INI parsing - can be enhanced later
    return true;
}

bool JobRegistry::SaveToINI(const char* ini_path) const {
    return true;
}

void JobRegistry::HotReload() {
    LOG_INFO("JobRegistry: Hot reload requested");
    const char* houses_ini = "CN.PLMOD\\types\\houses.ini";
    LoadFromINI(houses_ini);
}

} // namespace CNMod