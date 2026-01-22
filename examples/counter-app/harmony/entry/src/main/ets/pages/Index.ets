/**
 * CRAFT Auto-Generated ArkUI Page
 * Counter App - Adapted from Android Layout
 */

import { router } from '@kit.ArkUI';

// Application state using AppStorage for persistence
const counterKey = 'counter_value';

@Entry
@Component
struct Index {
    @State counter: number = 0;

    aboutToAppear(): void {
        // Restore state from AppStorage (equivalent to onRestoreInstanceState)
        const savedCounter = AppStorage.get<number>(counterKey);
        if (savedCounter !== undefined) {
            this.counter = savedCounter;
        }
    }

    aboutToDisappear(): void {
        // Save state to AppStorage (equivalent to onSaveInstanceState)
        AppStorage.setOrCreate(counterKey, this.counter);
    }

    build() {
        Column() {
            // Title
            Text('Counter App')
                .fontSize(28)
                .fontWeight(FontWeight.Bold)
                .fontColor('#333333')
                .margin({ bottom: 40 })

            // Counter Display
            Text(this.counter.toString())
                .fontSize(80)
                .fontWeight(FontWeight.Bold)
                .fontColor('#007AFF')
                .margin({ bottom: 60 })

            // Button Row
            Row() {
                // Decrement Button
                Button('-')
                    .width(90)
                    .height(90)
                    .fontSize(40)
                    .fontColor(Color.White)
                    .backgroundColor('#FF3B30')
                    .borderRadius(45)
                    .onClick(() => {
                        this.decrement();
                    })

                // Reset Button
                Button('0')
                    .width(90)
                    .height(90)
                    .fontSize(32)
                    .fontColor(Color.White)
                    .backgroundColor('#8E8E93')
                    .borderRadius(45)
                    .margin({ left: 20, right: 20 })
                    .onClick(() => {
                        this.reset();
                    })

                // Increment Button
                Button('+')
                    .width(90)
                    .height(90)
                    .fontSize(40)
                    .fontColor(Color.White)
                    .backgroundColor('#34C759')
                    .borderRadius(45)
                    .onClick(() => {
                        this.increment();
                    })
            }
            .justifyContent(FlexAlign.Center)

            // Footer
            Text('Powered by CRAFT Framework')
                .fontSize(14)
                .fontColor('#999999')
                .margin({ top: 60 })

            Text('Android -> HarmonyOS Adapter')
                .fontSize(12)
                .fontColor('#CCCCCC')
                .margin({ top: 8 })
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#FFFFFF')
    }

    /**
     * Increment counter - adapted from MainActivity.increment()
     */
    increment(): void {
        this.counter++;
        this.saveState();
    }

    /**
     * Decrement counter - adapted from MainActivity.decrement()
     */
    decrement(): void {
        this.counter--;
        this.saveState();
    }

    /**
     * Reset counter - adapted from MainActivity.reset()
     */
    reset(): void {
        this.counter = 0;
        this.saveState();
    }

    /**
     * Save state to persistent storage
     */
    private saveState(): void {
        AppStorage.setOrCreate(counterKey, this.counter);
    }
}
