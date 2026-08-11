#include "cpm/dds/ColorTypeObjectSupport.hpp"
#include "cpm/dds/CommonroadDDSGoalStateTypeObjectSupport.hpp"
#include "cpm/dds/CommonroadDDSShapeTypeObjectSupport.hpp"
#include "cpm/dds/CommonroadObstacleListTypeObjectSupport.hpp"
#include "cpm/dds/CommonroadObstacleTypeObjectSupport.hpp"
#include "cpm/dds/HeaderTypeObjectSupport.hpp"
#include "cpm/dds/HlcCommunicationTypeObjectSupport.hpp"
#include "cpm/dds/HLCHelloTypeObjectSupport.hpp"
#include "cpm/dds/LedPointsTypeObjectSupport.hpp"
#include "cpm/dds/LogLevelTypeObjectSupport.hpp"
#include "cpm/dds/LogTypeObjectSupport.hpp"
#include "cpm/dds/ParameterRequestTypeObjectSupport.hpp"
#include "cpm/dds/ParameterTypeObjectSupport.hpp"
#include "cpm/dds/Point2DTypeObjectSupport.hpp"
#include "cpm/dds/Pose2DTypeObjectSupport.hpp"
#include "cpm/dds/ReadyStatusTypeObjectSupport.hpp"
#include "cpm/dds/RoundTripTimeTypeObjectSupport.hpp"
#include "cpm/dds/StopRequestTypeObjectSupport.hpp"
#include "cpm/dds/SystemTriggerTypeObjectSupport.hpp"
#include "cpm/dds/TimeStampTypeObjectSupport.hpp"
#include "cpm/dds/VehicleCommandDirectTypeObjectSupport.hpp"
#include "cpm/dds/VehicleCommandTrajectoryTypeObjectSupport.hpp"
#include "cpm/dds/VehicleCommandPathTrackingTypeObjectSupport.hpp"
#include "cpm/dds/VehicleCommandSpeedCurvatureTypeObjectSupport.hpp"
#include "cpm/dds/VehicleObservationTypeObjectSupport.hpp"
#include "cpm/dds/VehicleStateListTypeObjectSupport.hpp"
#include "cpm/dds/VehicleStateTypeObjectSupport.hpp"
#include "cpm/dds/VisualizationTypeObjectSupport.hpp"

/**
 * TypeObject registration is now automatic in Fast DDS v3.
 * The registerXXXTypes() functions no longer exist.
 * This function is kept for backward compatibility but does nothing.
 **/
void register_type_objects(){
    // TypeObject registration is now automatic in Fast DDS v3
    // No manual registration needed
}
