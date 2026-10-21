package com.gathin.tvhome;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public final class JellyfinShowcase {
    private static final String TAG = "TvHome.JellyfinShowcase";
    public static final String SHOWCASE_DIR = "/sdcard/jellyfin_showcase";
    public static final String JELLYFIN_PKG = "org.jellyfin.androidtv";

    public static final class Movie {
        public final String id;
        public final String name;
        public final String year;
        public final String rating;
        public final String title;
        public final String tileFile;
        public final String backdropFile;

        public Movie(String id, String name, String year, String rating, String title, String tileFile, String backdropFile) {
            this.id = id;
            this.name = name;
            this.year = year;
            this.rating = rating;
            this.title = title;
            this.tileFile = tileFile;
            this.backdropFile = backdropFile;
        }
    }

    private final List<Movie> movies = new ArrayList<>();
    private int currentIndex = 0;
    private Bitmap currentBackdropBmp = null;
    private int loadedBackdropIndex = -1;
    private Context appContext;

    private static JellyfinShowcase instance;

    public static synchronized JellyfinShowcase get(Context ctx) {
        if (instance == null) {
            instance = new JellyfinShowcase();
            if (ctx != null) {
                instance.appContext = ctx.getApplicationContext();
                instance.loadMovies();
            }
        } else if (instance.appContext == null && ctx != null) {
            instance.appContext = ctx.getApplicationContext();
            if (!instance.hasMovies()) {
                instance.loadMovies();
            }
        }
        return instance;
    }

    private JellyfinShowcase() {}

    public synchronized void loadMovies() {
        movies.clear();
        InputStream is = null;
        File jsonFile = new File(SHOWCASE_DIR, "movies.json");
        try {
            if (jsonFile.exists() && jsonFile.canRead()) {
                is = new FileInputStream(jsonFile);
            }
        } catch (Exception ignored) {}

        if (is == null && appContext != null) {
            try {
                is = appContext.getAssets().open("jellyfin_showcase/movies.json");
            } catch (Exception e) {
                Log.e(TAG, "Cannot open assets movies.json", e);
            }
        }

        if (is != null) {
            try (InputStream input = is) {
                byte[] buf = new byte[input.available() > 0 ? input.available() : 16384];
                int read = input.read(buf);
                if (read > 0) {
                    String str = new String(buf, 0, read, StandardCharsets.UTF_8);
                    JSONArray arr = new JSONArray(str);
                    for (int i = 0; i < arr.length(); i++) {
                        JSONObject obj = arr.getJSONObject(i);
                        movies.add(new Movie(
                                obj.optString("id"),
                                obj.optString("name"),
                                obj.optString("year"),
                                obj.optString("rating"),
                                obj.optString("title"),
                                obj.optString("tile"),
                                obj.optString("backdrop")
                        ));
                    }
                    Log.i(TAG, "Loaded " + movies.size() + " showcase movies from Jellyfin");
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed parsing movies.json", e);
            }
        } else {
            Log.w(TAG, "No movies.json found in /sdcard or assets");
        }
    }

    public synchronized boolean hasMovies() {
        return !movies.isEmpty();
    }

    public synchronized int getMovieCount() {
        return movies.size();
    }

    public synchronized int getCurrentIndex() {
        return currentIndex;
    }

    public synchronized Movie getCurrentMovie() {
        if (movies.isEmpty()) return null;
        return movies.get(currentIndex % movies.size());
    }

    public synchronized Movie cycleNext() {
        if (movies.isEmpty()) return null;
        currentIndex = (currentIndex + 1) % movies.size();
        return getCurrentMovie();
    }

    public synchronized Movie cyclePrev() {
        if (movies.isEmpty()) return null;
        currentIndex = (currentIndex - 1 + movies.size()) % movies.size();
        return getCurrentMovie();
    }

    public synchronized Bitmap getCurrentTileBitmap(Context ctx) {
        Movie m = getCurrentMovie();
        if (m == null) return null;
        return loadTileBitmap(ctx != null ? ctx : appContext, m.tileFile);
    }

    public synchronized Drawable getCurrentTileDrawable(Context ctx) {
        Bitmap bmp = getCurrentTileBitmap(ctx);
        if (bmp == null) return null;
        return new BitmapDrawable((ctx != null ? ctx : appContext).getResources(), bmp);
    }

    public Bitmap loadTileBitmap(Context ctx, String filename) {
        File file = new File(SHOWCASE_DIR, filename);
        try {
            if (file.exists() && file.canRead()) {
                Bitmap bmp = BitmapFactory.decodeFile(file.getAbsolutePath());
                if (bmp != null) return bmp;
            }
        } catch (Exception ignored) {}

        Context c = ctx != null ? ctx : appContext;
        if (c != null) {
            try (InputStream is = c.getAssets().open("jellyfin_showcase/" + filename)) {
                return BitmapFactory.decodeStream(is);
            } catch (Exception | OutOfMemoryError e) {
                Log.e(TAG, "Error decoding asset tile " + filename, e);
            }
        }
        return null;
    }

    public synchronized Bitmap getCurrentBackdropBitmap(Context ctx, int displayWidth, int displayHeight) {
        Movie m = getCurrentMovie();
        if (m == null) return null;
        if (loadedBackdropIndex == currentIndex && currentBackdropBmp != null && !currentBackdropBmp.isRecycled()) {
            return currentBackdropBmp;
        }

        Bitmap newBmp = null;
        File file = new File(SHOWCASE_DIR, m.backdropFile);
        try {
            if (file.exists() && file.canRead()) {
                BitmapFactory.Options opts = new BitmapFactory.Options();
                opts.inPreferredConfig = Bitmap.Config.RGB_565;
                opts.inSampleSize = 1;
                newBmp = BitmapFactory.decodeFile(file.getAbsolutePath(), opts);
            }
        } catch (Exception ignored) {}

        Context c = ctx != null ? ctx : appContext;
        if (newBmp == null && c != null) {
            try (InputStream is = c.getAssets().open("jellyfin_showcase/" + m.backdropFile)) {
                BitmapFactory.Options opts = new BitmapFactory.Options();
                opts.inPreferredConfig = Bitmap.Config.RGB_565;
                opts.inSampleSize = 1;
                newBmp = BitmapFactory.decodeStream(is, null, opts);
            } catch (Exception | OutOfMemoryError e) {
                Log.e(TAG, "Error decoding asset backdrop " + m.backdropFile, e);
            }
        }

        if (newBmp != null) {
            Bitmap old = currentBackdropBmp;
            currentBackdropBmp = newBmp;
            loadedBackdropIndex = currentIndex;
            if (old != null && old != newBmp && !old.isRecycled()) {
                old.recycle();
            }
            return currentBackdropBmp;
        }
        return null;
    }

    public synchronized void releaseBackdrop() {
        if (currentBackdropBmp != null && !currentBackdropBmp.isRecycled()) {
            currentBackdropBmp.recycle();
            currentBackdropBmp = null;
            loadedBackdropIndex = -1;
        }
    }
}
