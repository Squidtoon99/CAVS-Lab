#pragma once
#include "../../low_level_controller/vehicle_atmega2560_firmware/spi_packets.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * \brief Initializes the PCA9685 PWM controller for motor and servo control.
 * \ingroup vehicle
 */
void spi_init();

/**
 * \brief Sends PWM commands to motor (throttle) and servo (steering) via PCA9685.
 *        Returns zero values for sensor data (no sensors connected).
 * \ingroup vehicle
 * 
 * \param spi_mosi_data The command data containing motor and steering values.
 * \param spi_miso_data_out After transfer is finished, this variable contains zeros
 *                          for all sensor fields (no sensors available).
 * \param n_transmission_attempts_out After transfer is finished, this variable indicates the
 *                                    number of transmission attempts (always 1 for PWM).
 * \param transmission_successful_out After transfer is finished, this flag indicates whether
 *                                    the PWM commands were sent successfully (1) or not (0).
 */
void spi_transfer(
    spi_mosi_data_t spi_mosi_data,
    spi_miso_data_t *spi_miso_data_out,
    int *n_transmission_attempts_out,
    int *transmission_successful_out
);

#ifdef __cplusplus
}
#endif