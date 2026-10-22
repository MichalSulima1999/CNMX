#pragma once

#ifndef CNMOD_INI_PARSER_H
#define CNMOD_INI_PARSER_H

#include <string>
#include <vector>
#include <map>
#include <variant>
#include <optional>

namespace CNMod {

// ============================================================================
// INI Parser for CN.PLMOD format
// ============================================================================

struct INIValue {
    std::string str;
    int64_t integer = 0;
    bool boolean = false;
    
    INIValue() = default;
    INIValue(const std::string& s) : str(s) { ParseInteger(); }
    INIValue(int64_t i) : integer(i) { str = std::to_string(i); }
    INIValue(bool b) : boolean(b) { str = b ? "1" : "0"; }
    
    void ParseInteger() {
        try {
            integer = std::stoll(str);
        } catch (...) {
            integer = 0;
        }
        boolean = (integer != 0 || str == "true" || str == "yes" || str == "on");
    }
    
    int GetInt() const { return static_cast<int>(integer); }
    int64_t GetInt64() const { return integer; }
    bool GetBool() const { return boolean; }
    const std::string& GetStr() const { return str; }
};

struct INIBlock {
    std::string name;
    std::map<std::string, INIValue> values;
    std::vector<INIBlock> children; // For nested blocks (not used in PLMOD)
    
    // Get value with default
    INIValue GetValue(const std::string& key, const INIValue& default_val = INIValue()) const {
        auto it = values.find(key);
        return (it != values.end()) ? it->second : default_val;
    }
    
    template<typename T>
    T Get(const std::string& key, const T& default_val) const {
        auto it = values.find(key);
        if (it == values.end()) return default_val;
        
        if constexpr (std::is_same_v<T, int>) return it->second.GetInt();
        else if constexpr (std::is_same_v<T, int64_t>) return it->second.GetInt64();
        else if constexpr (std::is_same_v<T, bool>) return it->second.GetBool();
        else if constexpr (std::is_same_v<T, std::string>) return it->second.GetStr();
        else return default_val;
    }
    
    int GetInt(const std::string& key, int default_val = 0) const {
        return Get<int>(key, default_val);
    }
    
    std::string GetString(const std::string& key, const std::string& default_val = "") const {
        return Get<std::string>(key, default_val);
    }
    
    bool GetBool(const std::string& key, bool default_val = false) const {
        return Get<bool>(key, default_val);
    }
    
    // Get multiple values with same key (e.g., multiple logicworker entries)
    std::vector<INIValue> GetMulti(const std::string& key) const {
        std::vector<INIValue> results;
        // In our simplified parser, we store multi-values in a special format
        // The actual implementation would need to track multiple entries
        // This is a simplified version - real implementation in parser
        return results;
    }
};

class INIParser {
public:
    INIParser() = default;
    
    bool Load(const std::string& filepath);
    bool LoadFromString(const std::string& content);
    
    // Get all blocks with given name
    std::vector<INIBlock> GetBlocks(const std::string& block_name) const {
        std::vector<INIBlock> result;
        for (const auto& block : blocks_) {
            if (block.name == block_name) {
                result.push_back(block);
            }
        }
        return result;
    }
    
    // Get first block with name
    std::optional<INIBlock> GetBlock(const std::string& block_name) const {
        for (const auto& block : blocks_) {
            if (block.name == block_name) return block;
        }
        return std::nullopt;
    }
    
    // Get all blocks
    const std::vector<INIBlock>& GetAllBlocks() const { return blocks_; }
    
private:
    std::vector<INIBlock> blocks_;
    std::string current_section_;
    
    void ParseLine(const std::string& line);
    std::string Trim(const std::string& str);
    std::pair<std::string, std::string> SplitKeyValue(const std::string& line);
    bool IsSectionHeader(const std::string& line, std::string& out_name);
};

struct INIMultiValue {
    // For keys that appear multiple times (logicworker, logicstock, logicproduction)
    struct WorkerEntry {
        uint32_t job_id = 0;
        uint32_t count = 0;
    };
    struct StockEntry {
        uint32_t good_id = 0;
        uint32_t qty = 0;
        uint32_t flags = 0;
        bool is_output = false;
    };
    
    std::vector<WorkerEntry> workers;
    std::vector<StockEntry> stocks;
    std::vector<uint32_t> production_goods;
};

} // namespace CNMod

#endif // CNMOD_INI_PARSER_H