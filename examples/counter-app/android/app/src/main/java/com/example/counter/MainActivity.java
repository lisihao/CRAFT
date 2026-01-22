package com.example.counter;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

/**
 * Simple Counter Application
 * Demonstrates Activity lifecycle management that will be adapted to HarmonyOS UIAbility.
 */
public class MainActivity extends Activity {

    private static final String KEY_COUNT = "counter_value";

    private int counter = 0;
    private TextView counterText;
    private Button incrementButton;
    private Button decrementButton;
    private Button resetButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize views
        counterText = findViewById(R.id.counter_text);
        incrementButton = findViewById(R.id.btn_increment);
        decrementButton = findViewById(R.id.btn_decrement);
        resetButton = findViewById(R.id.btn_reset);

        // Restore state if available
        if (savedInstanceState != null) {
            counter = savedInstanceState.getInt(KEY_COUNT, 0);
        }

        // Set up click listeners
        incrementButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                increment();
            }
        });

        decrementButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                decrement();
            }
        });

        resetButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                reset();
            }
        });

        updateDisplay();
    }

    @Override
    protected void onStart() {
        super.onStart();
        System.out.println("MainActivity: onStart");
    }

    @Override
    protected void onResume() {
        super.onResume();
        System.out.println("MainActivity: onResume");
    }

    @Override
    protected void onPause() {
        super.onPause();
        System.out.println("MainActivity: onPause");
    }

    @Override
    protected void onStop() {
        super.onStop();
        System.out.println("MainActivity: onStop");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("MainActivity: onDestroy");
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putInt(KEY_COUNT, counter);
        System.out.println("MainActivity: onSaveInstanceState, counter = " + counter);
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        counter = savedInstanceState.getInt(KEY_COUNT, 0);
        updateDisplay();
        System.out.println("MainActivity: onRestoreInstanceState, counter = " + counter);
    }

    /**
     * Increment the counter by 1
     */
    public void increment() {
        counter++;
        updateDisplay();
    }

    /**
     * Decrement the counter by 1
     */
    public void decrement() {
        counter--;
        updateDisplay();
    }

    /**
     * Reset the counter to 0
     */
    public void reset() {
        counter = 0;
        updateDisplay();
    }

    /**
     * Get current counter value
     */
    public int getCounter() {
        return counter;
    }

    /**
     * Update the display with current counter value
     */
    private void updateDisplay() {
        if (counterText != null) {
            counterText.setText(String.valueOf(counter));
        }
    }
}
