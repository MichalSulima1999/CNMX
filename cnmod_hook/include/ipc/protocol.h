#pragma once

#ifndef CNMOD_IPC_PROTOCOL_H
#define CNMOD_IPC_PROTOCOL_H

#include <cstdint>
#include <memory>
#include <string>

namespace CNMod {

enum class IPCCommand : uint32_t {
    REGISTER_JOB = 1,
    UNREGISTER_JOB = 2,
    REGISTER_PRODUCTION = 3,
    UNREGISTER_PRODUCTION = 4,
    REGISTER_GOOD = 5,
    UNREGISTER_GOOD = 6,
    REGISTER_UI_STRINGS = 7,
    HOT_RELOAD = 8,
    SAVE_CONFIG = 9,
    GET_STATUS = 10,
    GET_JOB_LIST = 11,
    GET_PRODUCTION_LIST = 12,
    GET_GOOD_LIST = 13,
};

struct IPCRequest {
    uint32_t command;
    uint32_t request_id;
    uint32_t payload_size;
    // uint8_t payload[]; // follows immediately
};

struct IPCResponse {
    uint32_t request_id;
    int32_t result;  // 0 = OK, <0 = error
    uint32_t payload_size;
    // uint8_t payload[]; // follows immediately
    
    // Non-serialized
    std::unique_ptr<uint8_t[]> payload;
    
    IPCResponse() : request_id(0), result(0), payload_size(0) {}
};

// Error codes
enum class IPCError : int32_t {
    OK = 0,
    INVALID_COMMAND = -1,
    PARSE_ERROR = -2,
    INVALID_PAYLOAD = -3,
    REGISTRY_ERROR = -4,
    NOT_FOUND = -5,
    ALREADY_EXISTS = -6,
    PERMISSION_DENIED = -7,
    INTERNAL_ERROR = -10,
    EXCEPTION = -11,
};

constexpr wchar_t PIPE_NAME[] = L"\\\\.\\pipe\\CNMod_ModdingAPI";
constexpr size_t PIPE_BUFFER_SIZE = 8192;
constexpr DWORD PIPE_TIMEOUT = 5000;

} // namespace CNMod

#endif // CNMOD_IPC_PROTOCOL_H