// INI Parser Implementation

#include "cnmod_hook.h"
#include "utils/ini_parser.h"
#include "utils/logging.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>

namespace CNMod {

bool INIParser::Load(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        LOG_ERROR("Cannot open INI file: %s", filepath.c_str());
        return false;
    }
    std::stringstream buffer;
    buffer << file.rdbuf();
    return LoadFromString(buffer.str());
}

bool INIParser::LoadFromString(const std::string& content) {
    blocks_.clear();
    current_section_.clear();
    
    std::istringstream stream(content);
    std::string line;
    while (std::getline(stream, line)) {
        line = Trim(line);
        if (line.empty() || line[0] == ';' || line[0] == '#') continue;
        
        std::string section_name;
        if (IsSectionHeader(line, current_section_)) continue;
        
        if (!current_section_.empty()) {
            auto [key, value] = SplitKeyValue(line);
            if (!key.empty()) {
                INIBlock* current_block = nullptr;
                for (auto& block : blocks_) {
                    if (block.name == current_section_) {
                        current_block = &block;
                        break;
                    }
                }
                if (!current_block) {
                    blocks_.emplace_back();
                    current_block = &blocks_.back();
                    current_block->name = current_section_;
                }
                current_block->values[key] = INIValue(value);
            }
        }
    }
    LOG_DEBUG("Parsed INI: %zu blocks", blocks_.size());
    return true;
}

std::string INIParser::Trim(const std::string& str) {
    size_t start = 0;
    while (start < str.size() && std::isspace(static_cast<unsigned char>(str[start]))) ++start;
    size_t end = str.size();
    while (end > start && std::isspace(static_cast<unsigned char>(str[end - 1])) ) --end;
    return str.substr(start, end - start);
}

std::pair<std::string, std::string> INIParser::SplitKeyValue(const std::string& line) {
    size_t eq = line.find('=');
    if (eq == std::string::npos) return {"", ""};
    std::string key = Trim(line.substr(0, eq));
    std::string value = Trim(line.substr(eq + 1));
    if (value.size() >= 2 && value.front() == '"' && value.back() == '"') {
        value = value.substr(1, value.size() - 2);
    }
    return {key, value};
}

bool INIParser::IsSectionHeader(const std::string& line, std::string& out_name) {
    if (line.size() >= 2 && line[0] == '[' && line.back() == ']') {
        out_name = line.substr(1, line.size() - 2);
        return true;
    }
    return false;
}

INIValue::INIValue(const std::string& s) : str(s) { ParseInteger(); }
INIValue::INIValue(int64_t i) : integer(i) { str = std::to_string(i); }
INIValue::INIValue(bool b) : boolean(b) { str = b ? "1" : "0"; }

void INIValue::ParseInteger() {
    try { integer = std::stoll(str); } catch (...) { integer = 0; }
    boolean = (integer != 0 || str == "true" || str == "yes" || str == "on");
}

} // namespace CNMod