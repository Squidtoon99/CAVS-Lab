#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <hiredis/hiredis.h>
#include "redis_comm.h"
#include "spi.h"

/**
 * \file redis_comm.c
 * \ingroup vehicle
 */

static redisContext *redis_ctx = NULL;
static bool hardware_initialized = false;

/**
 * \brief Checks if Redis connection is valid.
 */
static bool check_redis_connection() {
    if (redis_ctx == NULL || redis_ctx->err) {
        if (redis_ctx) {
            fprintf(stderr, "Redis connection error: %s\n", redis_ctx->errstr);
        } else {
            fprintf(stderr, "Redis connection is NULL\n");
        }
        return false;
    }
    return true;
}

void redis_init() {
    // Connect to Redis server on localhost:6379
    redis_ctx = redisConnect("127.0.0.1", 6379);
    
    if (redis_ctx == NULL || redis_ctx->err) {
        if (redis_ctx) {
            fprintf(stderr, "Redis connection error: %s\n", redis_ctx->errstr);
            redisFree(redis_ctx);
        } else {
            fprintf(stderr, "Can't allocate redis context\n");
        }
        exit(EXIT_FAILURE);
    }
    
    printf("Connected to Redis successfully\n");
    
    // Initialize PCA9685 PWM hardware
    spi_init();
    hardware_initialized = true;
    printf("PCA9685 hardware initialized\n");
}

void redis_transfer(
    spi_mosi_data_t spi_mosi_data,
    spi_miso_data_t *spi_miso_data_out,
    int *n_transmission_attempts_out,
    int *transmission_successful_out
)
{
    *transmission_successful_out = 0;
    *n_transmission_attempts_out = 1;
    
    // Send commands to actual hardware via PCA9685
    if (hardware_initialized) {
        spi_transfer(spi_mosi_data, spi_miso_data_out, n_transmission_attempts_out, transmission_successful_out);
    } else {
        fprintf(stderr, "Hardware not initialized\n");
        memset(spi_miso_data_out, 0, sizeof(spi_miso_data_t));
        return;
    }
    
    if (!check_redis_connection()) {
        // Hardware control succeeded but Redis logging failed - still return success
        return;
    }
    
    // Log command data to Redis for monitoring/debugging
    char cmd_key[64];
    snprintf(cmd_key, sizeof(cmd_key), "vehicle:%d:command", spi_mosi_data.vehicle_id);
    
    redisReply *reply = (redisReply*)redisCommand(redis_ctx, "SET %s %b", 
                                                   cmd_key, 
                                                   &spi_mosi_data, 
                                                   sizeof(spi_mosi_data_t));
    
    if (reply == NULL || redis_ctx->err) {
        fprintf(stderr, "Redis SET error: %s\n", redis_ctx->errstr);
        if (reply) freeReplyObject(reply);
        // Don't return - hardware control was successful
    } else {
        freeReplyObject(reply);
    }
    
    // Log sensor data to Redis for monitoring/debugging
    char sensor_key[64];
    snprintf(sensor_key, sizeof(sensor_key), "vehicle:%d:sensors", spi_mosi_data.vehicle_id);
    
    reply = (redisReply*)redisCommand(redis_ctx, "SET %s %b",
                                      sensor_key,
                                      spi_miso_data_out,
                                      sizeof(spi_miso_data_t));
    
    if (reply == NULL || redis_ctx->err) {
        fprintf(stderr, "Redis SET sensor error: %s\n", redis_ctx->errstr);
        if (reply) freeReplyObject(reply);
        // Don't return - hardware control was successful
    } else {
        freeReplyObject(reply);
    }
}

void redis_cleanup() {
    if (redis_ctx) {
        redisFree(redis_ctx);
        redis_ctx = NULL;
        printf("Redis connection closed\n");
    }
}
