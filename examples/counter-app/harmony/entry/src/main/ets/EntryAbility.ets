/**
 * CRAFT Auto-Generated UIAbility
 * Adapted from: com.example.counter.MainActivity
 */

import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';
import { MainActivityAdapter } from '../adapters/MainActivityAdapter';

const TAG = 'EntryAbility';
const DOMAIN = 0x0000;

export default class EntryAbility extends UIAbility {
    private adapter: MainActivityAdapter;
    private counter: number = 0;

    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        hilog.info(DOMAIN, TAG, 'onCreate');

        // Initialize the Android compatibility adapter
        this.adapter = new MainActivityAdapter(this);

        // Restore state from Want if available
        if (want.parameters && want.parameters['counter_value']) {
            this.counter = want.parameters['counter_value'] as number;
        }

        // Call Android-style onCreate via adapter
        this.adapter.onCreate();
    }

    onDestroy(): void {
        hilog.info(DOMAIN, TAG, 'onDestroy');
        this.adapter.onDestroy();
    }

    onWindowStageCreate(windowStage: window.WindowStage): void {
        hilog.info(DOMAIN, TAG, 'onWindowStageCreate');

        this.adapter.setWindowStage(windowStage);

        // Load the main page
        windowStage.loadContent('pages/Index', (err) => {
            if (err.code) {
                hilog.error(DOMAIN, TAG, 'Failed to load content: %{public}s', JSON.stringify(err));
                return;
            }
            hilog.info(DOMAIN, TAG, 'Content loaded successfully');
        });
    }

    onWindowStageDestroy(): void {
        hilog.info(DOMAIN, TAG, 'onWindowStageDestroy');
    }

    onForeground(): void {
        hilog.info(DOMAIN, TAG, 'onForeground');
        // Maps to Android onStart + onResume
        this.adapter.onStart();
        this.adapter.onResume();
    }

    onBackground(): void {
        hilog.info(DOMAIN, TAG, 'onBackground');
        // Maps to Android onPause + onStop
        this.adapter.onPause();
        this.adapter.onStop();
    }

    onSaveState(reason: AbilityConstant.StateType): AbilityConstant.OnSaveResult {
        hilog.info(DOMAIN, TAG, 'onSaveState, reason: %{public}d', reason);
        // Corresponds to Android onSaveInstanceState
        this.adapter.onSaveInstanceState();
        return AbilityConstant.OnSaveResult.ALL_AGREE;
    }

    // Expose counter operations for the UI
    getCounter(): number {
        return this.counter;
    }

    setCounter(value: number): void {
        this.counter = value;
    }
}
