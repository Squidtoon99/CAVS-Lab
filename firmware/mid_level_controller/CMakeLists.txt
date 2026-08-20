project(vehicle_rpi_firmware)

include_directories(src)
include_directories(${CMAKE_SOURCE_DIR}/cpm_lib/include/)
include_directories(${CMAKE_SOURCE_DIR}/cpm_lib/include/cpm/)
include_directories(${CMAKE_SOURCE_DIR}/cpm_lib/dds_idl_cpp/)

set(SOURCE_BASE
    src/main.cxx
    src/SensorCalibration.cxx
    src/SensorCalibration.hpp
    src/Localization.cxx
    src/Localization.hpp
    src/Controller.cxx
    src/Controller.hpp
    src/TrajectoryInterpolation.cxx
    src/TrajectoryInterpolation.hpp
    src/PathInterpolation.cxx
    src/PathInterpolation.hpp
    src/casadi_mpc_fn.c
    src/casadi_mpc_fn.h
    src/redis_comm.c
    src/redis_comm.h
    src/MpcController.hpp
    src/MpcController.cxx
    src/PathTrackingController.hpp
    src/PathTrackingController.cxx
    src/VehicleModel.hpp
    src/VehicleModel.cxx
    ${CMAKE_SOURCE_DIR}/low_level_controller/vehicle_atmega2560_firmware/crc.h
    ${CMAKE_SOURCE_DIR}/low_level_controller/vehicle_atmega2560_firmware/crc.c
)

set_source_files_properties(src/casadi_mpc_fn.c PROPERTIES COMPILE_FLAGS -O3)

if(BUILD_SIMULATION)
    set(SOURCE
        ${SOURCE_BASE}
        src/geometry.hpp
        src/SimulationVehicle.cxx
        src/SimulationVehicle.hpp
        src/SimulationIPS.cxx
        src/SimulationIPS.hpp
    )
else()
    set(SOURCE
        ${SOURCE_BASE}
        src/bcm2835.c
        src/bcm2835.h
        src/spi.cxx
        src/spi.h
    )
endif()

add_executable(vehicle_rpi_firmware ${SOURCE})

if(BUILD_ARM)
    target_compile_options(vehicle_rpi_firmware PUBLIC -fpic)
else()
    target_compile_options(vehicle_rpi_firmware PUBLIC -fpic -Wl,--no-as-needed)
    set_target_properties(vehicle_rpi_firmware PROPERTIES LINK_FLAGS "-Wl,--no-as-needed")
endif()

if(BUILD_SIMULATION)
    target_compile_options(vehicle_rpi_firmware PUBLIC -DVEHICLE_SIMULATION)
endif()

if(BUILD_ARM)
    target_link_libraries(vehicle_rpi_firmware cpm fastdds stdc++fs PiPCA9685 bcm2835 hiredis i2c)
else()
    target_link_libraries(vehicle_rpi_firmware cpm fastdds fastcdr foonathan_memory PiPCA9685 i2c hiredis)
endif()
