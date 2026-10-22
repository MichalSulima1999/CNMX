// UI Registry Implementation

#include "cnmod_hook.h"
#include "utils/logging.h"

namespace CNMod {

UIRegistry& UIRegistry::Instance() {
    static UIRegistry instance;
    return instance;
}

bool UIRegistry::RegisterUIStrings(const UIStrings& strings) {
    if (!strings.IsValid()) return false;
    
    std::lock_guard<std::mutex> lock(mutex_);
    ui_strings_[strings.job_id] = strings;
    LOG_INFO("Registered UI strings for job %u: %s", strings.job_id, strings.ui_name);
    return true;
}

bool UIRegistry::UnregisterUIStrings(uint32_t job_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = ui_strings_.find(job_id);
    if (it == ui_strings_.end()) return false;
    ui_strings_.erase(it);
    return true;
}

UIStrings* UIRegistry::GetUIStrings(uint32_t job_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = ui_strings_.find(job_id);
    return (it != ui_strings_.end()) ? &it->second : nullptr;
}

const UIStrings* UIRegistry::GetUIStrings(uint32_t job_id) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = ui_strings_.find(job_id);
    return (it != ui_strings_.end()) ? &it->second : nullptr;
}

bool UIRegistry::LoadFromDLL() {
    LOG_INFO("UIRegistry: LoadFromDLL - hook into DLL for job names");
    return false;
}

void UIRegistry::HotReload() {
    LOG_INFO("UIRegistry: Hot reload");
}

} // namespace CNMod