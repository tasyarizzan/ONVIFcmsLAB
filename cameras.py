from onvif import ONVIFCamera
from time import sleep


long_line = ""
for i in range(80):
    long_line += "-"


class Camera:
    def __init__(self, ip, port, login, password):
        # Connecting to the camera
        self.my_cam = ONVIFCamera(
            ip,
            port,
            login,
            password
        )

        # Creating media service
        self.media_service = self.my_cam.create_media_service()

        
        # Getting profiles
        self.profiles = self.media_service.GetProfiles()
        self.media_profile = self.profiles[0]

        # Creating PTZ service
        self.ptz = self.my_cam.create_ptz_service()

        # Getting ptz move options
        self.request_absolute_move = self.ptz.create_type("AbsoluteMove")
        self.request_absolute_move.ProfileToken = self.media_profile._token


        self.request_continuous_move = self.ptz.create_type("ContinuousMove")
        self.request_continuous_move.ProfileToken = self.media_profile._token


        self.request_relative_move = self.ptz.create_type("RelativeMove")
        self.request_relative_move.ProfileToken = self.media_profile._token

        self.request_stop = self.ptz.create_type("Stop")
        self.request_stop.ProfileToken = self.media_profile._token

        # Creating imaging service
        self.imaging = self.my_cam.create_imaging_service()

        # Getting imaging move options
        self.request_focus_change = self.imaging.create_type("Move")
        self.request_focus_change.VideoSourceToken = self.media_profile.VideoSourceConfiguration.SourceToken

        self.stop()

    # Print debug information
    def get_debug_info(self):

        # Getting device information
        print("Device information: " + str(self.my_cam.devicemgmt.GetDeviceInformation()))
        print(long_line)

        # Getting hostname
        print("Device hostname: " + str(self.my_cam.devicemgmt.GetHostname().Name))
        print(long_line)

        # Getting system date and time
        dt = self.my_cam.devicemgmt.GetSystemDateAndTime()
        tz = dt.TimeZone
        year = dt.UTCDateTime.Date.Year
        hour = dt.UTCDateTime.Time.Hour

        print("Timezone: " + str(tz))
        print("Year: " + str(year))
        print("Hour: " + str(hour))
        print(long_line)

        print("Profiles: " + str(self.profiles))
        print(long_line)

        print("Token: " + str(self.media_profile._token))
        print(long_line)

        # Getting available PTZ services
        request = self.ptz.create_type("GetServiceCapabilities")
        ptz_service_capabilities = self.ptz.GetServiceCapabilities(request)

        print("Service capabilities: " + str(ptz_service_capabilities))
        print(long_line)

        # Getting PTZ status
        ptz_status = self.ptz.GetStatus({"ProfileToken": self.media_profile._token})

        print("PTZ status: " + str(ptz_status))
        print(long_line)
        print("Pan position:" + str(ptz_status.Position.PanTilt._x))
        print("Tilt position:" + str(ptz_status.Position.PanTilt._y))
        print("Zoom position:" + str(ptz_status.Position.Zoom._x))
        try:
            print("Pan/Tilt Moving?:" + str(ptz_status.MoveStatus.PanTilt))
        except:
            pass
        print(long_line)

        # Getting PTZ configuration options for getting option ranges
        request = self.ptz.create_type("GetConfigurationOptions")
        request.ConfigurationToken = self.media_profile.PTZConfiguration._token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        print("PTZ configuration options: " + str(ptz_configuration_options))
        print(long_line)

        print("Continuous move options: " + str(self.request_continuous_move))
        print(long_line)

        print("Absolute move options: " + str(self.request_absolute_move))
        print(long_line)

        print("Relative move options: " + str(self.request_relative_move))
        print(long_line)

        print("Stop options: " + str(self.request_stop))
        print(long_line)

        # Getting available imaging services
        request = self.imaging.create_type("GetServiceCapabilities")
        imaging_service_capabilities = self.ptz.GetServiceCapabilities(request)

        print("Service capabilities: " + str(imaging_service_capabilities))
        print(long_line)

        # Getting imaging status
        imaging_status = self.imaging.GetStatus({"VideoSourceToken": self.media_profile.VideoSourceConfiguration.SourceToken})

        print("Imaging status: " + str(imaging_status))
        print(long_line)

        print("Focus move options: " + str(self.request_focus_change))
        print(long_line)

    # "--------------------------------------------------------------------------------"

    # Get position of the camera
    def get_ptz_position(self):
        # Getting PTZ status
        status = self.ptz.GetStatus({"ProfileToken": self.media_profile._token})

        print(long_line)
        print("PTZ position: " + str(status.Position))
        print(long_line)

    def get_focus_options(self):
        # Getting imaging status
        imaging_status = self.imaging.GetStatus({"VideoSourceToken": self.media_profile.VideoSourceConfiguration.SourceToken})

        print(long_line)
        # Getting available imaging services
        request = self.imaging.create_type("GetServiceCapabilities")
        imaging_service_capabilities = self.ptz.GetServiceCapabilities(request)

        print("Service capabilities: " + str(imaging_service_capabilities))
        print(long_line)
        print("Imaging status: " + str(imaging_status))
        print(long_line)

    # "--------------------------------------------------------------------------------"

    # Stop any movement
    def stop(self):
        self.request_stop.PanTilt = True
        self.request_stop.Zoom = True

        self.ptz.Stop(self.request_stop)

    # "--------------------------------------------------------------------------------"

    # Continuous move functions
    def perform_continuous_move(self, timeout):
        # Start continuous move
        self.ptz.ContinuousMove(self.request_continuous_move)

        sleep(timeout)

        self.stop()

        sleep(2)

    def move_continuous_tilt(self, velocity, timeout):
        print("Tilting with velocity: \"" +
              str(velocity) +
              "\" and timeout: \"" +
              str(timeout) +
              "\""
              )

        status = self.ptz.GetStatus({"ProfileToken": self.media_profile._token})
        status.Position.PanTilt._x = 0.0
        status.Position.PanTilt._y = velocity

        self.request_continuous_move.Velocity = status.Position

        self.perform_continuous_move(timeout)

    def move_continuous_pan(self, velocity, timeout):
        print("Panning with velocity: \"" +
              str(velocity) +
              "\" and timeout: \"" +
              str(timeout) +
              "\""
              )

        status = self.ptz.GetStatus({"ProfileToken": self.media_profile._token})
        status.Position.PanTilt._x = velocity
        status.Position.PanTilt._y = 0.0

        self.request_continuous_move.Velocity = status.Position

        self.perform_continuous_move(timeout)

    def move_continuous_diagonal(self, velocity_x, velocity_y, timeout):
        print("Moving diagonally with velocities: \"" +
              str(velocity_x) + ":" + str(velocity_y) +
              "\" and timeout: \"" +
              str(timeout) +
              "\""
              )

        status = self.ptz.GetStatus({"ProfileToken": self.media_profile._token})
        status.Position.PanTilt._x = velocity_x
        status.Position.PanTilt._y = velocity_y

        self.request_continuous_move.Velocity = status.Position

        self.perform_continuous_move(timeout)

    def move_continuous_zoom(self, velocity, timeout):
        print("Zooming with velocity: \"" +
              str(velocity) +
              "\" and timeout: \"" +
              str(timeout) +
              "\""
              )

        status = self.ptz.GetStatus({"ProfileToken": self.media_profile._token})
        status.Position.Zoom._x = velocity

        self.request_continuous_move.Velocity = status.Position

        self.perform_continuous_move(timeout)

    def move_continuous_custom(self,
                               velocity_one, timeout_one,
                               velocity_two, timeout_two,
                               velocity_three, timeout_three):

        self.move_continuous_pan(velocity_one, timeout_one)
        self.move_continuous_tilt(velocity_two, timeout_two)
        self.move_continuous_zoom(velocity_three, timeout_three)

    # "--------------------------------------------------------------------------------"

    # Absolute move functions
    def perform_absolute_move(self):
        # Start absolute move
        self.ptz.AbsoluteMove(self.request_absolute_move)

        sleep(4)

    def move_absolute(self, x, y, zoom):
        print("Moving to: \"" +
              str(x) + ":" + str(y) + ":" + str(zoom) +
              "\""
              )

        status = self.ptz.GetStatus({"ProfileToken": self.media_profile._token})
        status.Position.PanTilt._x = x
        status.Position.PanTilt._y = y
        status.Position.Zoom._x = zoom

        self.request_absolute_move.Position = status.Position

        self.perform_absolute_move()

    # "--------------------------------------------------------------------------------"

    # Focus change functions
    def change_focus_continuous(self, speed, timeout):
        print("Changing focus with speed: \"" +
              str(speed) +
              "\" and timeout: \"" +
              str(timeout) +
              "\""
              )

        self.request_focus_change.Focus = {
            "Continuous": {
                "Speed": speed
            }
        }

        self.imaging.Move(self.request_focus_change)

        sleep(timeout)

        self.stop()

        sleep(2)

    def change_focus_absolute(self, position, speed):
        print("Changing focus to: \"" +
              str(position) +
              "\" with speed: \"" +
              str(speed) +
              "\""
              )

        self.request_focus_change.Focus = {
            "Absolute": {
                "Position": position,
                "Speed": speed
            }
        }

        self.imaging.Move(self.request_focus_change)

        sleep(4)
