// Good Registry Implementation

#include "cnmod_hook.h"
#include "utils/logging.h"

namespace CNMod {

GoodRegistry& GoodRegistry::Instance() {
    static GoodRegistry instance;
    return instance;
}

bool GoodRegistry::RegisterGood(const GoodDefinition& good) {
    if (!good.IsValid()) {
        LOG_ERROR("Invalid good definition: good_id=%u", good.good_id);
        return false;
    }
    
    std::lock_guard<std::mutex> lock(mutex_);
    goods_[good.good_id] = good;
    LOG_INFO("Registered good %u: %s", good.good_id, good.name);
    return true;
}

bool GoodRegistry::UnregisterGood(uint32_t good_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = goods_.find(good_id);
    if (it == goods_.end()) return false;
    goods_.erase(it);
    LOG_INFO("Unregistered good %u", good_id);
    return true;
}

GoodDefinition* GoodRegistry::GetGood(uint32_t good_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = goods_.find(good_id);
    return (it != goods_.end()) ? &it->second : nullptr;
}

const GoodDefinition* GoodRegistry::GetGood(uint32_t good_id) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = goods_.find(good_id);
    return (it != goods_.end()) ? &it->second : nullptr;
}

std::vector<uint32_t> GoodRegistry::GetAllGoodIds() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<uint32_t> ids;
    ids.reserve(goods_.size());
    for (const auto& pair : goods_) {
        ids.push_back(pair.first);
    }
    return ids;
}

bool GoodRegistry::LoadFromINI(const char* ini_path) {
    LOG_INFO("Loading goods from %s", ini_path);
    return true;
}

void GoodRegistry::HotReload() {
    LOG_INFO("GoodRegistry: Hot reload");
    const char* ini = "Data\\logic\\goodtypes.ini";
    LoadFromINI(ini);
}

} // namespace CNMod