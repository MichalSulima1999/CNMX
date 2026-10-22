// Test file for CNMod Hook System

#include "cnmod_hook.h"
#include <iostream>
#include <cassert>

using namespace CNMod;

int main() {
    std::cout << "=== CNMod Hook System Test ===" << std::endl;
    
    // Test 1: JobRegistry
    std::cout << "\n[Test 1] JobRegistry..." << std::endl;
    auto& job_reg = JobRegistry::Instance();
    
    JobDefinition job;
    job.job_id = 26;
    strcpy_s(job.name, "Smolarz");
    job.building_type = 57;
    job.output_good = 66;
    job.input_goods[0] = 5;
    job.input_counts[0] = 10;
    job.worker_count = 1;
    
    assert(job_reg.RegisterJob(job));
    std::cout << "  Registered job 26" << std::endl;
    
    auto* retrieved = job_reg.GetJob(26);
    assert(retrieved != nullptr);
    assert(strcmp(retrieved->name, "Smolarz") == 0);
    assert(retrieved->building_type == 57);
    assert(retrieved->output_good == 66);
    assert(retrieved->worker_count == 1);
    std::cout << "  Retrieved job 26 successfully" << std::endl;
    
    auto all_jobs = job_reg.GetAllJobIds();
    assert(std::find(all_jobs.begin(), all_jobs.end(), 26) != all_jobs.end());
    std::cout << "  Job list contains job 26" << std::endl;
    
    // Test 2: ProductionRegistry
    std::cout << "\n[Test 2] ProductionRegistry..." << std::endl;
    auto& prod_reg = ProductionRegistry::Instance();
    
    ProductionChain chain;
    chain.building_type = 57;
    chain.output_good = 66;
    chain.input_goods[0] = 5;
    chain.input_counts[0] = 10;
    chain.production_time = 100;
    chain.worker_job = 26;
    chain.max_workers = 1;
    
    assert(prod_reg.RegisterProduction(chain));
    std::cout << "  Registered production for building 57" << std::endl;
    
    auto* retrieved_chain = prod_reg.GetProduction(57);
    assert(retrieved_chain != nullptr);
    assert(retrieved_chain->output_good == 66);
    std::cout << "  Retrieved production for building 57" << std::endl;
    
    // Test 3: GoodRegistry
    std::cout << "\n[Test 3] GoodRegistry..." << std::endl;
    auto& good_reg = GoodRegistry::Instance();
    
    GoodDefinition good;
    good.good_id = 66;
    strcpy_s(good.name, "wegiel");
    good.type = 12;
    good.is_input = true;
    good.is_produced_in_house = true;
    good.atomic_for_production = 1;
    
    assert(good_reg.RegisterGood(good));
    std::cout << "  Registered good 66" << std::endl;
    
    auto* retrieved_good = good_reg.GetGood(66);
    assert(retrieved_good != nullptr);
    assert(strcmp(retrieved_good->name, "wegiel") == 0);
    std::cout << "  Retrieved good 66" << std::endl;
    
    // Test 4: UIRegistry
    std::cout << "\n[Test 4] UIRegistry..." << std::endl;
    auto& ui_reg = UIRegistry::Instance();
    
    UIStrings ui;
    ui.job_id = 26;
    strcpy_s(ui.ui_name, "Smolarz");
    strcpy_s(ui.ui_description, "Produkuje węgiel z drewna");
    
    assert(ui_reg.RegisterUIStrings(ui));
    std::cout << "  Registered UI strings for job 26" << std::endl;
    
    auto* retrieved_ui = ui_reg.GetUIStrings(26);
    assert(retrieved_ui != nullptr);
    assert(strcmp(retrieved_ui->ui_name, "Smolarz") == 0);
    std::cout << "  Retrieved UI strings for job 26" << std::endl;
    
    // Test 5: INI Parser
    std::cout << "\n[Test 5] INI Parser..." << std::endl;
    INIParser parser;
    
    // Test parsing a simple INI
    std::string ini_content = R"(
[logichousetype]
debugname "test_building"
logictype 100
logicmaintype 3
logicworker 50 1
logicstock 5 10 1
logicstock 66 15 0
logicproduction 66
debugcolor 100 0 0
)";
    
    INIParser parser;
    assert(parser.LoadFromString(ini_content));
    
    auto blocks = parser.GetBlocks("logichousetype");
    assert(blocks.size() == 1);
    
    auto& block = blocks[0];
    assert(block.GetInt("logictype") == 100);
    assert(block.GetString("debugname") == "test_building");
    std::cout << "  Parsed INI block successfully" << std::endl;
    
    // Test 5: Hot Reload
    std::cout << "\n[Test 5] Hot Reload..." << std::endl;
    RequestHotReload();
    assert(g_hot_reload_requested.load());
    ProcessHotReload();
    assert(!g_hot_reload_requested.load());
    std::cout << "  Hot reload request processed" << std::endl;
    
    std::cout << "\n=== All Tests Passed! ===" << std::endl;
    return 0;
}