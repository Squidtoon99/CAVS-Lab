#ifndef _CRC_H_
#define _CRC_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifndef TRUE
#define FALSE 0
#define TRUE  !FALSE
#endif

/*
 * Select CRC-CCITT standard (16-bit)
 */
typedef uint16_t crc;

#define CRC_NAME            "CRC-CCITT"
#define POLYNOMIAL          0x1021
#define INITIAL_REMAINDER   0xFFFF
#define FINAL_XOR_VALUE     0x0000
#define REFLECT_DATA        FALSE
#define REFLECT_REMAINDER   FALSE
#define CHECK_VALUE         0x29B1

/* Function Prototypes */
void crcInit(void);
crc  crcFast(uint8_t const message[], int nBytes);

#ifdef __cplusplus
}
#endif

#endif /* _CRC_H_ */
