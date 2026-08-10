#ifndef RTMAPS_TYPES_H
#define RTMAPS_TYPES_H

/* ------------------------------------------ */
/* - Defines                                - */
/* ------------------------------------------ */

/**
 * Data offset: checksum (int32)
 */
#define DSA_HEADER_CHECKSUM_OFFSET  0

/**
 * Data offset: counter (uint8)
 */
#define DSA_HEADER_COUNTER_OFFSET   4

/**
 * Data offset: timestamp (uint64)
 */
#define DSA_HEADER_TIMESTAMP_OFFSET 8

/**
 * Data offset: payload
 */
#define DSA_HEADER_PAYLOAD_OFFSET   16

/* ------------------------------------------ */
/* - Typedefs                               - */
/* ------------------------------------------ */
#if defined(_DS1401) || defined(_DS1403) || defined(_DS1202) || defined(_DS1203) || defined (DS_PLATFORM_SMARTHIL) || defined(VEOS_PLATFORM)
    #include <tmwtypes.h>

	#ifndef UINT64_T
		typedef unsigned long long uint64_T;
	#endif
#elif defined (MATLAB_MEX_FILE)
    #include <simstruc.h>
#elif defined (RTMAPS_PLATFORM)
	#include <stdint.h>

	typedef uint64_t uint64_T;
	typedef int64_t int64_T;
	typedef uint32_t uint32_T;
	typedef int32_t int32_T;
	typedef int16_t int16_T;
	typedef uint16_t uint16_T;
	typedef int8_t int8_T;
	typedef uint8_t uint8_T;
	typedef bool boolean_T;
#else
    #error Unsupported platform
#endif

typedef float single;

#endif /* RTMAPS_TYPES_H */


