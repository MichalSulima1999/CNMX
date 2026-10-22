// Production Registry Implementation

#include "cnmod_hook.h"
#include "utils/logging.h"

namespace CNMod {

ProductionRegistry& ProductionRegistry::Instance() {
    static ProductionRegistry instance;
    return instance;
}

bool ProductionRegistry::RegisterProduction(const ProductionChain& chain) {
    if (!chain.IsValid()) {
        LOG_ERROR("Invalid production chain: building_type=%u", chain.building_type);
        return false;
    }
    
    std::lock_guard<std::mutex> lock(mutex_);
    chains_[chain.building_type] = chain;
    LOG_INFO("Registered production for building %u: output=%u", chain.building_type, chain.output_good);
    return true;
}

bool ProductionRegistry::UnregisterProduction(uint32_t building_type) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = chains_.find(building_type);
    if (it == chains_.end()) return false;
    chains_.erase(it);
    LOG_INFO("Unregistered production for building %u", building_type);
    return true;
}

ProductionChain* ProductionRegistry::GetProduction(uint32_t building_type) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = chains_.find(building_type);
    return (it != chains_.end()) ? &it->second : nullptr;
}

const ProductionChain* ProductionRegistry::GetProduction(uint32_t building_type) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = chains_.find(building_type);
    return (it != chains_.end()) ? &it->second : nullptr;
}

std::vector<uint32_t> ProductionRegistry::GetAllBuildingTypes() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<uint32_t> types;
    types.reserve(chains_.size());
    for (const auto& pair : chains_) {
        types.push_back(pair.first);
    }
    return types;
}

bool ProductionRegistry::LoadFromINI(const char* ini_path) {
    LOG_INFO("Loading productions from %s", ini_path);
    return true;
}

void ProductionRegistry::HotReload() {
    LOG_INFO("ProductionRegistry: Hot reload");
    const char* ini = "CN.PLMOD\\types\\houses.ini";
    LoadFromINI(ini);
}

} // namespace CNMod