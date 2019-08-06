from __future__ import print_function, division
import time
import atexit
import os

from modular_client import ModularClient

try:
    from pkg_resources import get_distribution, DistributionNotFound
    _dist = get_distribution('sleep_assay_testing')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'sleep_assay_testing')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except (ImportError,DistributionNotFound):
    __version__ = None
else:
    __version__ = _dist.version


DEBUG = False

class SleepAssayTesting():
    '''
    SleepAssayTesting.

    Example Usage:

    dev = SleepAssayTesting()
    '''

    def __init__(self,*args,**kwargs):
        atexit.register(self._exit_sleep_assay_testing)
        print('Locating modular clients...')
        self.controller = ModularClient()

    def test_assay(self):
        print('Testing assay')

        print('Setting time')
        self.controller.set_time(time.time())
        time.sleep(1)

        print('Setting properties')
        self.controller.camera_trigger_frequency('setValue',1)
        self.controller.entrainment_duration('setValue',3)
        self.controller.recovery_duration('setValue',1)
        self.controller.white_light_on_duration('setValue',12)
        self.controller.white_light_entrainment_power('setValue',10)
        self.controller.white_light_recovery_power('setValue',10)
        self.controller.visible_backlight_frequency('setValue',2)
        self.controller.visible_backlight_duty_cycle('setValue',4)

        experiment_day = self.controller.add_experiment_day()
        self.controller.set_experiment_day_visible_backlight(experiment_day,10,0,24)
        self.controller.set_experiment_day_white_light(experiment_day,10)
        print(self.controller.get_experiment_info())
        print()
        time.sleep(4)

        self.controller.test_assay()

        assay_status = self.controller.get_assay_status()
        while assay_status['phase'] != 'ASSAY_FINISHED':
            assay_status = self.controller.get_assay_status()
            print('phase: {0}'.format(assay_status['phase']))
            print('assay_day: {0}'.format(assay_status['assay_day']))
            print('phase_day: {0}'.format(assay_status['phase_day']))
            print('white_light_power: {0}'.format(assay_status['white_light_power']))
            print('visible_backlight_intensity: {0}'.format(assay_status['visible_backlight_intensity']))
            print()
            time.sleep(1)

    def _exit_sleep_assay_testing(self):
        pass


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':

    dev = SleepAssayTesting()
    dev.test_assay()
