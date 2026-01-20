/*
 * Copyright (C) 2006 The Android Open Source Project
 * Sample Activity class for CRAFT testing
 */
package android.app;

import android.os.Bundle;
import android.view.View;
import android.content.Intent;

/**
 * An activity is a single, focused thing that the user can do.
 * This is a simplified version for testing purposes.
 */
public class Activity extends ContextThemeWrapper implements Window.Callback {

    private String mTitle;
    private boolean mFinished;

    /**
     * Called when the activity is starting.
     * @param savedInstanceState If the activity is being re-initialized after
     *     previously being shut down then this Bundle contains the data it most
     *     recently supplied in onSaveInstanceState(Bundle).
     */
    protected void onCreate(Bundle savedInstanceState) {
        // Base implementation
    }

    /**
     * Called after onCreate(Bundle) or onRestart() when the activity is
     * being started.
     */
    protected void onStart() {
        // Base implementation
    }

    /**
     * Called after onStart() when the activity is becoming visible to the user.
     */
    protected void onResume() {
        // Base implementation
    }

    /**
     * Called when the system is about to start resuming a previous activity.
     */
    protected void onPause() {
        // Base implementation
    }

    /**
     * Called when the activity is no longer visible to the user.
     */
    protected void onStop() {
        // Base implementation
    }

    /**
     * Perform any final cleanup before an activity is destroyed.
     */
    protected void onDestroy() {
        // Base implementation
    }

    /**
     * Called to retrieve per-instance state from an activity before being killed.
     * @param outState Bundle in which to place your saved state.
     */
    protected void onSaveInstanceState(Bundle outState) {
        // Base implementation
    }

    /**
     * This method is called after onStart() when the activity is
     * being re-initialized from a previously saved state.
     * @param savedInstanceState the data most recently supplied in onSaveInstanceState(Bundle).
     */
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        // Base implementation
    }

    /**
     * Change the title associated with this activity.
     * @param title The new title
     */
    public void setTitle(CharSequence title) {
        this.mTitle = title.toString();
    }

    /**
     * Return the title of this activity.
     * @return The current title
     */
    public CharSequence getTitle() {
        return mTitle;
    }

    /**
     * Call this when your activity is done and should be closed.
     */
    public void finish() {
        mFinished = true;
    }

    /**
     * Check whether this activity is finishing.
     * @return true if the activity is finishing
     */
    public boolean isFinishing() {
        return mFinished;
    }

    /**
     * Launch a new activity.
     * @param intent The intent to start
     */
    public void startActivity(Intent intent) {
        // Start activity implementation
    }

    /**
     * Launch an activity for which you would like a result when it finished.
     * @param intent The intent to start
     * @param requestCode Request code to identify the result
     */
    public void startActivityForResult(Intent intent, int requestCode) {
        // Start activity for result implementation
    }

    /**
     * Set the result that your activity will return to its caller.
     * @param resultCode The result code to propagate back
     */
    public void setResult(int resultCode) {
        // Set result implementation
    }

    /**
     * Set the result that your activity will return to its caller.
     * @param resultCode The result code to propagate back
     * @param data The data to propagate back
     */
    public void setResult(int resultCode, Intent data) {
        // Set result with data implementation
    }

    /**
     * Finds a view that was identified by the id attribute.
     * @param id The id to search for
     * @return The view if found or null otherwise
     */
    public View findViewById(int id) {
        return null;
    }
}
