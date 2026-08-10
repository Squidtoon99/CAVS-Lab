#ifndef DSA_GEN_DirectCommandTest_H
#define DSA_GEN_DirectCommandTest_H

/* ------------------------------------------ */
/* - Includes                               - */
/* ------------------------------------------ */
#include "rtmaps_functions.h"

/* ------------------------------------------ */
/* - Defines                                - */
/* ------------------------------------------ */
/* #define DSA_PACK_STRUCTURES */

/* ------------------------------------------ */
/* - Struct                                 - */
/* ------------------------------------------ */
#ifdef DSA_PACK_STRUCTURES
#pragma pack(push, 1)
#endif
typedef struct {
    uint8_T vehicle_id;
    double motor_throttle;
    double steering_servo;
} DirectCommandTest;
#define DEFINED_TYPEDEF_FOR_DirectCommandTest_
#ifdef DSA_PACK_STRUCTURES
#pragma pack(pop)
#endif

#ifdef DSA_PACK_STRUCTURES
#pragma pack(push, 1)
#endif
typedef struct {
    int32_T   crc;
    uint8_T   counter;
    uint8_T   padding1;
    uint16_T  padding2;
    uint64_T  timestamp;
    DirectCommandTest payload;
} DirectCommandTest_Wrapper;
#ifdef DSA_PACK_STRUCTURES
#pragma pack(pop)
#endif

#endif
