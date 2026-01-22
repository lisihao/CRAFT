/**
 * CRAFT 自动生成 - Android API 适配器
 * 源自: com.example.counter.MainActivity
 *
 * API 风格: OpenHarmony (@ohos.xxx)
 * 兼容: OpenHarmony 3.2+ / HarmonyOS 3.0+
 *
 * 提供 Android Activity API 兼容层
 */

import UIAbility from '@ohos.app.ability.UIAbility';
import common from '@ohos.app.ability.common';
import hilog from '@ohos.hilog';

const TAG: string = 'MainActivityAdapter';
const DOMAIN: number = 0x0000;

/**
 * Android Activity API 适配器
 *
 * 将 Android API 调用委托给 OpenHarmony API:
 * - finish() -> terminateSelf()
 * - onCreate() -> onCreate()
 * - onDestroy() -> onDestroy()
 */
export class MainActivityAdapter {
    private context: common.UIAbilityContext;

    constructor(context: common.UIAbilityContext) {
        this.context = context;
    }

    /**
     * 对应 Android: Activity.finish()
     * 功能: 关闭当前 Activity/Ability 窗口
     *
     * Android 实现:
     *   public void finish() {
     *       // 关闭 Activity，触发 onDestroy
     *   }
     *
     * OpenHarmony 实现:
     *   terminateSelf() - 关闭当前 UIAbility
     */
    finish(): void {
        hilog.info(DOMAIN, TAG, 'finish() called -> terminateSelf()');
        this.context.terminateSelf();
    }

    /**
     * 对应 Android: Activity.onCreate(Bundle)
     */
    onCreate(): void {
        hilog.info(DOMAIN, TAG, 'onCreate() called');
    }

    /**
     * 对应 Android: Activity.onDestroy()
     */
    onDestroy(): void {
        hilog.info(DOMAIN, TAG, 'onDestroy() called');
    }
}
