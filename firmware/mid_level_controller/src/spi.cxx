#include <PiPCA9685/PCA9685.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include "spi.h"

/**
 * \file spi.cxx
 * \ingroup vehicle
 */

// PWM Configuration
#define PWM_FREQ 60.0
#define PWM_THROTTLE_CHANNEL 0
#define PWM_STEERING_CHANNEL 1

#define STEERING_LEFT_PWM 460
#define STEERING_RIGHT_PWM 290
#define STEERING_CENTER_PWM ((STEERING_LEFT_PWM + STEERING_RIGHT_PWM) / 2)

#define THROTTLE_FORWARD_PWM 500
#define THROTTLE_STOPPED_PWM 340
#define THROTTLE_REVERSE_PWM 220

// Global PCA9685 controller instance
static PiPCA9685::PCA9685* pca = NULL;

/**
 * \brief Maps a normalized steering value (-1 to 1) to PWM value
 * \param steering_normalized Normalized steering value: -1 (left) to 1 (right)
 * \return PWM value for steering servo
 */
static int map_steering_to_pwm(double steering_normalized) {
    // steering_normalized: -1 = full left, 0 = center, 1 = full right
    // PWM: 460 = left, 375 = center, 290 = right
    if (steering_normalized < -1.0) steering_normalized = -1.0;
    if (steering_normalized > 1.0) steering_normalized = 1.0;
    
    // Map -1 to STEERING_LEFT_PWM and 1 to STEERING_RIGHT_PWM
    return (int)(STEERING_CENTER_PWM - steering_normalized * (STEERING_LEFT_PWM - STEERING_CENTER_PWM));
}

/**
 * \brief Maps motor throttle value to PWM value based on motor mode
 * \param motor_pwm_raw Raw motor PWM value (0-400)
 * \param motor_mode Motor mode (forward, reverse, brake)
 * \return PWM value for throttle ESC
 */
static int map_throttle_to_pwm(int16_t motor_pwm_raw, uint8_t motor_mode) {
    if (motor_mode == SPI_MOTOR_MODE_BRAKE || motor_mode == 0) {
        return THROTTLE_STOPPED_PWM;
    }
    
    // motor_pwm_raw is 0-400, need to map to appropriate range
    double normalized = motor_pwm_raw / 400.0; // 0 to 1
    if (normalized < 0.0) normalized = 0.0;
    if (normalized > 1.0) normalized = 1.0;
    
    if (motor_mode == SPI_MOTOR_MODE_FORWARD) {
        // Map 0-1 to STOPPED-FORWARD
        return (int)(THROTTLE_STOPPED_PWM + normalized * (THROTTLE_FORWARD_PWM - THROTTLE_STOPPED_PWM));
    } else if (motor_mode == SPI_MOTOR_MODE_REVERSE) {
        // Map 0-1 to STOPPED-REVERSE
        return (int)(THROTTLE_STOPPED_PWM - normalized * (THROTTLE_STOPPED_PWM - THROTTLE_REVERSE_PWM));
    }
    
    return THROTTLE_STOPPED_PWM;
}

void spi_init() {
    try {
        pca = new PiPCA9685::PCA9685();
        pca->set_pwm_freq(PWM_FREQ);
        
        // Initialize both channels to safe stopped state
        pca->set_pwm(PWM_THROTTLE_CHANNEL, 0, THROTTLE_STOPPED_PWM);
        pca->set_pwm(PWM_STEERING_CHANNEL, 0, STEERING_CENTER_PWM);
        
        printf("PCA9685 initialized successfully\n");
    } catch (const std::exception& e) {
        printf("Failed to initialize PCA9685: %s\n", e.what());
        exit(EXIT_FAILURE);
    }
}


void spi_transfer(
    spi_mosi_data_t spi_mosi_data,
    spi_miso_data_t *spi_miso_data_out,
    int *n_transmission_attempts_out,
    int *transmission_successful_out
)
{
    *transmission_successful_out = 1;
    *n_transmission_attempts_out = 1;

    if (pca == NULL) {
        *transmission_successful_out = 0;
        return;
    }

    try {
        // Map and send throttle command
        int throttle_pwm = map_throttle_to_pwm(spi_mosi_data.motor_pwm, spi_mosi_data.motor_mode);
        pca->set_pwm(PWM_THROTTLE_CHANNEL, 0, throttle_pwm);
        
        // Map and send steering command
        // servo_command is already in a scaled format, need to convert to normalized
        // Original code: spi_mosi_data.servo_command = int16_t(steering_servo * (-1200.0));
        // So steering_servo = servo_command / (-1200.0)
        double steering_normalized = spi_mosi_data.servo_command / (-1200.0);
        int steering_pwm = map_steering_to_pwm(steering_normalized);
        pca->set_pwm(PWM_STEERING_CHANNEL, 0, steering_pwm);

        // Clear sensor data structure and return zeros
        memset(spi_miso_data_out, 0, sizeof(spi_miso_data_t));
        
        // Set some reasonable default values
        spi_miso_data_out->tick = 0;
        spi_miso_data_out->odometer_steps = 0;
        spi_miso_data_out->imu_yaw = 0;
        spi_miso_data_out->imu_yaw_rate = 0;
        spi_miso_data_out->imu_acceleration_forward = 0;
        spi_miso_data_out->imu_acceleration_left = 0;
        spi_miso_data_out->imu_acceleration_up = 0;
        spi_miso_data_out->speed = 0;
        spi_miso_data_out->battery_voltage = 0;
        spi_miso_data_out->motor_current = 0;
        spi_miso_data_out->CRC = 0;
        spi_miso_data_out->status_flags = 0; // No errors
                                                                
    } catch (const std::exception& e) {
        printf("PCA9685 communication error: %s\n", e.what());
        *transmission_successful_out = 0;
    }
}
