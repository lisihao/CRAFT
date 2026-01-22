/**
 * CRAFT 自动生成 - UIAbility
 * 源自: com.example.counter.MainActivity
 *
 * API 映射:
 * - Activity.onCreate() -> UIAbility.onCreate()
 * - Activity.finish() -> UIAbilityContext.terminateSelf()
 * - Activity.onDestroy() -> UIAbility.onDestroy()
 */

import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';

const TAG = 'EntryAbility';
const DOMAIN = 0x0000;

export default class EntryAbility extends UIAbility {

    /**
     * 对应 Android: Activity.onCreate(Bundle)
     * 功能: 初始化 Ability
     */
    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        hilog.info(DOMAIN, TAG, 'onCreate - 窗口创建');
    }

    /**
     * HarmonyOS 特有: 窗口舞台创建
     * 对应 Android: Activity.setContentView()
     */
    onWindowStageCreate(windowStage: window.WindowStage): void {
        hilog.info(DOMAIN, TAG, 'onWindowStageCreate - 加载页面');

        // 加载主页面 (对应 setContentView)
        windowStage.loadContent('pages/Index', (err) => {
            if (err.code) {
                hilog.error(DOMAIN, TAG, '页面加载失败: %{public}s', JSON.stringify(err));
                return;
            }
            hilog.info(DOMAIN, TAG, '页面加载成功');
        });
    }

    /**
     * 对应 Android: Activity.onDestroy()
     * 功能: 释放资源
     */
    onDestroy(): void {
        hilog.info(DOMAIN, TAG, 'onDestroy - 窗口关闭');
    }

    onWindowStageDestroy(): void {
        hilog.info(DOMAIN, TAG, 'onWindowStageDestroy');
    }

    onForeground(): void {
        hilog.info(DOMAIN, TAG, 'onForeground - 进入前台');
    }

    onBackground(): void {
        hilog.info(DOMAIN, TAG, 'onBackground - 进入后台');
    }
}
