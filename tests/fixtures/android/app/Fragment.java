/*
 * Copyright (C) 2010 The Android Open Source Project
 * Sample Fragment class for CRAFT testing
 */
package android.app;

import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.content.Context;

/**
 * A Fragment is a piece of an application's user interface or behavior
 * that can be placed in an Activity.
 */
public class Fragment {

    private Activity mActivity;
    private View mView;
    private boolean mAttached;

    /**
     * Called when a fragment is first attached to its context.
     * @param context The context to attach to
     */
    public void onAttach(Context context) {
        mAttached = true;
    }

    /**
     * Called to do initial creation of a fragment.
     * @param savedInstanceState If the fragment is being re-created from
     *     a previous saved state, this is the state.
     */
    public void onCreate(Bundle savedInstanceState) {
        // Fragment creation
    }

    /**
     * Called to have the fragment instantiate its user interface view.
     * @param inflater The LayoutInflater object that can be used to inflate views
     * @param container The parent view that the fragment's UI should be attached to
     * @param savedInstanceState Previous saved state
     * @return Return the View for the fragment's UI, or null.
     */
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        return null;
    }

    /**
     * Called immediately after onCreateView has returned.
     * @param view The View returned by onCreateView
     * @param savedInstanceState Previous saved state
     */
    public void onViewCreated(View view, Bundle savedInstanceState) {
        mView = view;
    }

    /**
     * Called when the fragment is visible to the user and actively running.
     */
    public void onResume() {
        // Fragment resumed
    }

    /**
     * Called when the Fragment is no longer resumed.
     */
    public void onPause() {
        // Fragment paused
    }

    /**
     * Called when the view previously created by onCreateView has been detached.
     */
    public void onDestroyView() {
        mView = null;
    }

    /**
     * Called when the fragment is no longer in use.
     */
    public void onDestroy() {
        // Fragment destroyed
    }

    /**
     * Called when the fragment is no longer attached to its activity.
     */
    public void onDetach() {
        mAttached = false;
        mActivity = null;
    }

    /**
     * Return the Activity this fragment is currently associated with.
     * @return The associated Activity
     */
    public Activity getActivity() {
        return mActivity;
    }

    /**
     * Return the view this fragment is associated with.
     * @return The fragment's root view
     */
    public View getView() {
        return mView;
    }

    /**
     * Return true if the fragment is currently added to its activity.
     * @return true if added
     */
    public boolean isAdded() {
        return mAttached && mActivity != null;
    }

    /**
     * Look for a child view with the given id.
     * @param id The id to search for
     * @return The view if found or null
     */
    public View findViewById(int id) {
        if (mView != null) {
            return mView.findViewById(id);
        }
        return null;
    }
}
