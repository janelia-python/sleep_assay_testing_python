from __future__ import print_function, division
import time
import atexit
import os
import json
from datetime import datetime
import argparse
import matplotlib.pyplot as plt

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

    def test_assay(self):
        print('Testing assay')

        print('Locating modular clients...')
        self.controller = ModularClient()

        self.controller.set_time(1565375039.191516)

        print('Setting properties')
        self.controller.camera_trigger_frequency('setValue',1)
        self.controller.entrainment_duration('setValue',3)
        self.controller.recovery_duration('setValue',1)
        self.controller.white_light_on_duration('setValue',12)
        self.controller.white_light_entrainment_power('setValue',10)
        self.controller.white_light_recovery_power('setValue',10)
        self.controller.visible_backlight_frequency('setValue',2)
        self.controller.visible_backlight_duty_cycle('setValue',4)

        self.controller.remove_all_experiment_days()
        experiment_day = self.controller.add_experiment_day()
        self.controller.set_experiment_day_visible_backlight(experiment_day,10,0,24)
        self.controller.set_experiment_day_white_light(experiment_day,10)
        print()
        time.sleep(4)

        test_count = 1000
        test = 0
        while test < test_count:
            self.controller.set_time(1565375039.191516)
            time.sleep(1)

            now = datetime.now().isoformat(timespec='minutes')
            print("starting test {0} at {1}".format(test,now))

            self.controller.test_assay()

            assay_status_list = []
            assay_status = self.controller.get_assay_status()
            while assay_status['phase'] != 'ASSAY_FINISHED':
                assay_status = self.controller.get_assay_status()
                assay_status.pop('time_now')
                assay_status.pop('date_time_now')
                assay_status_list.append(assay_status)
                time.sleep(1)
            if test == 0:
                with open('test_data.json','w') as json_file:
                    json.dump(assay_status_list,json_file,indent=2)
            else:
                with open('test_data.json','r') as json_file:
                    test_data = json.load(json_file)
                if assay_status_list == test_data:
                    print('test {} matched test 0'.format(test))
                else:
                    print('test {} did not match test 0!!!'.format(test))
                    with open('test_data_{}.json'.format(test),'w') as json_file:
                        json.dump(assay_status_list,json_file,indent=2)
            test += 1

    def plot_assay_data(self):
        with open('test_data.json','r') as json_file:
            good_test_data = json.load(json_file)
        t = [sample['assay_day'] for sample in good_test_data]
        white_light_power = [sample['white_light_power'] for sample in good_test_data]
        plt.step(t,white_light_power,label='good')

        offset_delta = 100.0
        offset = 0.0
        data_files = [f for f in os.listdir('.') if os.path.isfile(f) and 'test_data_' in f]
        for data_file in data_files:
            offset += offset_delta
            with open(data_file,'r') as json_file:
                bad_test_data = json.load(json_file)
            white_light_power = [sample['white_light_power'] + offset for sample in bad_test_data]
            plt.step(t,white_light_power,label=data_file.replace('test_data_','').replace('.json',''))

        plt.legend()
        plt.show()



    def _exit_sleep_assay_testing(self):
        pass


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':

    dev = SleepAssayTesting()

    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--test',
                        help='Test assay.',
                        action='store_true')
    parser.add_argument('-p','--plot',
                        help='Plot assay test results.',
                        action='store_true')
    args = parser.parse_args()

    if args.plot:
        dev.plot_assay_data()
    elif args.test:
        dev.test_assay()
    else:
        parser.print_help()
