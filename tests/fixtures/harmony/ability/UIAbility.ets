/*
 * Copyright (c) Huawei Technologies Co., Ltd.
 * Sample UIAbility class for CRAFT testing
 */

import Want from '@ohos.app.ability.Want';
import AbilityConstant from '@ohos.app.ability.AbilityConstant';
import window from '@ohos.window';

/**
 * UIAbility is the base class for abilities that have a UI.
 * It provides lifecycle callbacks for managing the ability's window stage.
 */
export default class UIAbility {
    private context: Context;
    private windowStage: window.WindowStage | null = null;

    /**
     * Called when the ability is created.
     * @param want Information about the ability
     * @param launchParam Launch parameters
     */
    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        console.log('UIAbility onCreate');
    }

    /**
     * Called when the ability is destroyed.
     */
    onDestroy(): void {
        console.log('UIAbility onDestroy');
    }

    /**
     * Called when the window stage is created.
     * @param windowStage The window stage instance
     */
    onWindowStageCreate(windowStage: window.WindowStage): void {
        this.windowStage = windowStage;
        console.log('UIAbility onWindowStageCreate');
    }

    /**
     * Called when the window stage is destroyed.
     */
    onWindowStageDestroy(): void {
        this.windowStage = null;
        console.log('UIAbility onWindowStageDestroy');
    }

    /**
     * Called when the ability moves to the foreground.
     */
    onForeground(): void {
        console.log('UIAbility onForeground');
    }

    /**
     * Called when the ability moves to the background.
     */
    onBackground(): void {
        console.log('UIAbility onBackground');
    }

    /**
     * Called when a new Want is received.
     * @param want The new Want
     * @param launchParam Launch parameters
     */
    onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        console.log('UIAbility onNewWant');
    }

    /**
     * Get the context of this ability.
     * @returns The ability context
     */
    getContext(): Context {
        return this.context;
    }

    /**
     * Get the window stage of this ability.
     * @returns The window stage or null
     */
    getWindowStage(): window.WindowStage | null {
        return this.windowStage;
    }

    /**
     * Terminate this ability.
     * @returns Promise that resolves when terminated
     */
    terminateSelf(): Promise<void> {
        return new Promise((resolve) => {
            console.log('UIAbility terminateSelf');
            resolve();
        });
    }

    /**
     * Terminate this ability with a result.
     * @param parameter The result parameter
     * @returns Promise that resolves when terminated
     */
    terminateSelfWithResult(parameter: AbilityResult): Promise<void> {
        return new Promise((resolve) => {
            console.log('UIAbility terminateSelfWithResult');
            resolve();
        });
    }

    /**
     * Start another ability.
     * @param want The Want describing the ability to start
     * @returns Promise that resolves when the ability is started
     */
    startAbility(want: Want): Promise<void> {
        return new Promise((resolve) => {
            console.log('UIAbility startAbility');
            resolve();
        });
    }

    /**
     * Start another ability and get a result.
     * @param want The Want describing the ability to start
     * @returns Promise that resolves with the result
     */
    startAbilityForResult(want: Want): Promise<AbilityResult> {
        return new Promise((resolve) => {
            console.log('UIAbility startAbilityForResult');
            resolve({ resultCode: 0 });
        });
    }
}

interface AbilityResult {
    resultCode: number;
    want?: Want;
}

interface Context {
    // Context interface
}
