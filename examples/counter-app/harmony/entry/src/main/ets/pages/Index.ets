/**
 * CRAFT 自动生成 - ArkUI 页面
 * 对应 Android: activity_main.xml + MainActivity.java
 *
 * API 风格: OpenHarmony (@ohos.xxx)
 * 兼容: OpenHarmony 3.2+ / HarmonyOS 3.0+
 *
 * 功能:
 * 1. 显示 "Hello World" 文本
 * 2. 点击按钮关闭窗口
 *
 * API 映射:
 * - TextView -> Text 组件
 * - Button -> Button 组件
 * - Button.setOnClickListener() -> Button.onClick()
 * - Activity.finish() -> terminateSelf()
 */

import common from '@ohos.app.ability.common';
import hilog from '@ohos.hilog';

const TAG: string = 'IndexPage';
const DOMAIN: number = 0x0000;

@Entry
@Component
struct Index {

    /**
     * 获取 UIAbility 上下文
     * 用于调用 terminateSelf() 关闭窗口
     */
    private context: common.UIAbilityContext = getContext(this) as common.UIAbilityContext;

    /**
     * 构建 UI
     * 对应 Android: activity_main.xml
     */
    build() {
        // Column 对应 Android LinearLayout (vertical)
        Column() {

            // Text 对应 Android TextView
            // android:text="Hello World"
            Text('Hello World')
                .fontSize(32)
                .fontWeight(FontWeight.Bold)
                .fontColor('#333333')
                .margin({ bottom: 48 })

            // Button 对应 Android Button
            // android:id="@+id/btn_close"
            Button('关闭窗口')
                .width(200)
                .height(60)
                .fontSize(18)
                .fontColor(Color.White)
                .backgroundColor('#FF3B30')
                .borderRadius(8)
                .onClick(() => {
                    this.closeWindow();
                })

        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#FFFFFF')
    }

    /**
     * 关闭窗口
     * 对应 Android: Activity.finish()
     *
     * Android 代码:
     *   finish();
     *
     * OpenHarmony 代码:
     *   this.context.terminateSelf();
     */
    closeWindow(): void {
        hilog.info(DOMAIN, TAG, '关闭窗口 - 对应 Activity.finish()');

        // terminateSelf() 对应 Android finish()
        this.context.terminateSelf((err) => {
            if (err.code) {
                hilog.error(DOMAIN, TAG, '关闭失败: %{public}s', JSON.stringify(err));
                return;
            }
            hilog.info(DOMAIN, TAG, '窗口已关闭');
        });
    }
}
