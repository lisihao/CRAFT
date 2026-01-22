package com.example.counter;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

/**
 * Simple Hello World Application
 *
 * 功能:
 * 1. 显示 "Hello World" 文本
 * 2. 点击按钮关闭窗口
 *
 * 演示 Android API:
 * - Activity.onCreate(Bundle) - 创建界面
 * - Activity.finish() - 关闭 Activity
 * - View.setOnClickListener() - 按钮点击事件
 */
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 获取关闭按钮
        Button closeButton = findViewById(R.id.btn_close);

        // 设置点击事件: 关闭窗口
        closeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 调用 finish() 关闭当前 Activity
                finish();
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("MainActivity: Window closed");
    }
}
