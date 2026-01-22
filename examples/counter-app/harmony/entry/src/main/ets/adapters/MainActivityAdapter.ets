/**
 * CRAFT Auto-Generated Adapter
 * Source: com.example.counter.MainActivity
 *
 * This adapter provides Android Activity API compatibility over HarmonyOS UIAbility.
 */

import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';

const TAG = 'MainActivityAdapter';
const DOMAIN = 0x0000;

/**
 * Adapter providing Android MainActivity API compatibility.
 * Delegates lifecycle and state management to UIAbility.
 */
export class MainActivityAdapter {
    private context: UIAbility;
    private windowStage: window.WindowStage | null = null;

    // State fields adapted from Android
    private KEY_COUNT: string;
    private counter: number;
    private counterText: Object;
    private incrementButton: Object;
    private decrementButton: Object;
    private resetButton: Object;

    constructor(context: UIAbility) {
        this.context = context;
        this.KEY_COUNT = "";
        this.counter = 0;
        this.counterText = null;
        this.incrementButton = null;
        this.decrementButton = null;
        this.resetButton = null;
    }

    /**
     * Get the UIAbility context
     */
    getContext(): UIAbility {
        return this.context;
    }

    /**
     * Set the WindowStage for UI operations
     */
    setWindowStage(windowStage: window.WindowStage): void {
        this.windowStage = windowStage;
    }

    /**
     * Lifecycle: onCreate -> onCreate
     * Bundle data should be passed via Want.parameters
     */
    onCreate(): void {
        hilog.info(DOMAIN, TAG, 'onCreate called (maps to onCreate)');
    }

    /**
     * Adapted method: onClick
     */
    onClick(v: Object): void {
        hilog.info(DOMAIN, TAG, 'onClick called');
    }

    /**
     * Adapted method: onClick
     */
    onClick(v: Object): void {
        hilog.info(DOMAIN, TAG, 'onClick called');
    }

    /**
     * Adapted method: onClick
     */
    onClick(v: Object): void {
        hilog.info(DOMAIN, TAG, 'onClick called');
    }

    /**
     * Lifecycle: onStart -> onForeground
     * Android onStart maps to HarmonyOS onForeground
     */
    onStart(): void {
        hilog.info(DOMAIN, TAG, 'onStart called (maps to onForeground)');
    }

    /**
     * Lifecycle: onResume -> onForeground
     * Android onResume also maps to onForeground (combined state)
     */
    onResume(): void {
        hilog.info(DOMAIN, TAG, 'onResume called (maps to onForeground)');
    }

    /**
     * Lifecycle: onPause -> onBackground
     * Android onPause maps to HarmonyOS onBackground
     */
    onPause(): void {
        hilog.info(DOMAIN, TAG, 'onPause called (maps to onBackground)');
    }

    /**
     * Lifecycle: onStop -> onBackground
     * Android onStop also maps to onBackground (combined state)
     */
    onStop(): void {
        hilog.info(DOMAIN, TAG, 'onStop called (maps to onBackground)');
    }

    /**
     * Lifecycle: onDestroy -> onDestroy
     * Direct mapping
     */
    onDestroy(): void {
        hilog.info(DOMAIN, TAG, 'onDestroy called (maps to onDestroy)');
    }

    /**
     * Lifecycle: onSaveInstanceState -> onSaveState
     * Use AppStorage or PersistentStorage for state
     */
    onSaveInstanceState(): void {
        hilog.info(DOMAIN, TAG, 'onSaveInstanceState called (maps to onSaveState)');
    }

    /**
     * Lifecycle: onRestoreInstanceState -> onCreate
     * Restore from Want.parameters or storage
     */
    onRestoreInstanceState(): void {
        hilog.info(DOMAIN, TAG, 'onRestoreInstanceState called (maps to onCreate)');
    }

    /**
     * Adapted method: increment
     */
    increment(): void {
        hilog.info(DOMAIN, TAG, 'increment called');
    }

    /**
     * Adapted method: decrement
     */
    decrement(): void {
        hilog.info(DOMAIN, TAG, 'decrement called');
    }

    /**
     * Adapted method: reset
     */
    reset(): void {
        hilog.info(DOMAIN, TAG, 'reset called');
    }

    /**
     * Adapted method: getCounter
     */
    getCounter(): number {
        hilog.info(DOMAIN, TAG, 'getCounter called');
        return 0;
    }
}
