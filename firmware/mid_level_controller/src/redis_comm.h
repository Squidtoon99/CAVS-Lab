#pragma once
#include "../../low_level_controller/vehicle_atmega2560_firmware/spi_packets.h"

/**
 * \brief Sets up Redis connection for vehicle communication.
 * \ingroup vehicle
 */
void redis_init();

/**
 * \brief Exchanges data with the low_level_controller via Redis.
 *        Commands are written to Redis, sensor data is read from Redis.
 * \ingroup vehicle
 * 
 * \param spi_mosi_data The command package to be sent to low_level_controller.
 * \param spi_miso_data_out After transfer is finished, this variable contains the received
 *                          sensor data from low_level_controller.
 * \param n_transmission_attempts_out After transfer is finished, this variable indicates the
 *                                    number of transmission attempts which were needed (always 1 for Redis).
 * \param transmission_successful_out After transfer is finished, this flag indicates whether
 *                                    the transmission was successful (1) or not (0).
 */
void redis_transfer(
    spi_mosi_data_t spi_mosi_data,
    spi_miso_data_t *spi_miso_data_out,
    int *n_transmission_attempts_out,
    int *transmission_successful_out
);

/**
 * \brief Cleanup Redis connection.
 * \ingroup vehicle
 */
void redis_cleanup();
