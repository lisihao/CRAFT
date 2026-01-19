# 百度贴吧 App API 桥接清单

> 详细列出需要桥接的 Android API 及其 HarmonyOS 对应方案

---

## 一、必须桥接的核心 API (P0 - 阻塞性)

### 1.1 应用生命周期 API

| Android API | HarmonyOS 对应 | 桥接复杂度 | 优先级 |
|------------|---------------|-----------|--------|
| `android.app.Activity` | `@ohos.app.ability.UIAbility` | 高 | P0 |
| `android.app.Application` | `AbilityStage` | 中 | P0 |
| `android.content.Intent` | `@ohos.app.ability.Want` | 中 | P0 |
| `android.os.Bundle` | `Record<string, Object>` | 低 | P0 |
| `android.content.Context` | `@ohos.app.ability.common.Context` | 高 | P0 |

**Activity 生命周期映射详表**:

```
Android                    HarmonyOS UIAbility
───────────────────────    ────────────────────────────
onCreate(Bundle)       →   onWindowStageCreate(WindowStage)
onStart()              →   (无直接对应，合并到 onForeground)
onResume()             →   onForeground()
onPause()              →   onBackground()
onStop()               →   (无直接对应，合并到 onBackground)
onDestroy()            →   onWindowStageDestroy()
onRestart()            →   onForeground() (从后台返回)

onSaveInstanceState()  →   onSaveState()
onRestoreInstanceState() → onSaveState() 读取

onActivityResult()     →   Caller 机制 / Want 返回
startActivity()        →   context.startAbility()
startActivityForResult() → context.startAbilityForResult()
finish()               →   context.terminateSelf()
```

### 1.2 UI 基础组件 API

| Android API | HarmonyOS 对应 | 桥接方案 |
|------------|---------------|---------|
| `android.view.View` | `CommonMethod` (ArkUI 基类) | 创建 ViewCompat 桥接类 |
| `android.view.ViewGroup` | `Column/Row/Stack` | 布局容器映射 |
| `android.widget.TextView` | `Text` 组件 | 属性映射 |
| `android.widget.Button` | `Button` 组件 | 直接映射 |
| `android.widget.ImageView` | `Image` 组件 | 属性映射 |
| `android.widget.EditText` | `TextInput/TextArea` | 事件映射 |
| `android.widget.ProgressBar` | `Progress` 组件 | 属性映射 |
| `android.widget.Switch` | `Toggle` 组件 | 属性映射 |
| `android.widget.CheckBox` | `Checkbox` 组件 | 属性映射 |

**View 属性映射表**:

```
Android View 属性              ArkUI 对应
────────────────────────      ────────────────────────
setVisibility(VISIBLE)    →   .visibility(Visibility.Visible)
setVisibility(GONE)       →   .visibility(Visibility.None)
setBackgroundColor()      →   .backgroundColor()
setPadding()              →   .padding()
setLayoutParams()         →   .width() / .height()
setOnClickListener()      →   .onClick()
setOnLongClickListener()  →   .gesture(LongPressGesture)
setEnabled()              →   .enabled()
setAlpha()                →   .opacity()
```

### 1.3 列表组件 API (贴吧核心)

| Android API | HarmonyOS 对应 | 说明 |
|------------|---------------|------|
| `RecyclerView` | `List` + `LazyForEach` | 需要 Adapter 模式转换 |
| `RecyclerView.Adapter` | `IDataSource` | 数据源接口映射 |
| `RecyclerView.ViewHolder` | `@Reusable` 装饰器 | 复用机制不同 |
| `LinearLayoutManager` | `List` (vertical) | 默认垂直 |
| `GridLayoutManager` | `Grid` / `lanes` 属性 | 网格布局 |
| `StaggeredGridLayoutManager` | `WaterFlow` | 瀑布流 |
| `ItemDecoration` | `divider` 属性 | 分隔线 |
| `DiffUtil` | `LazyForEach` 自动 diff | 数据更新 |

**RecyclerView 桥接示例**:

```java
// Android 原始代码
public class PostAdapter extends RecyclerView.Adapter<PostViewHolder> {
    private List<Post> posts;

    @Override
    public PostViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
            .inflate(R.layout.item_post, parent, false);
        return new PostViewHolder(view);
    }

    @Override
    public void onBindViewHolder(PostViewHolder holder, int position) {
        Post post = posts.get(position);
        holder.title.setText(post.getTitle());
        holder.content.setText(post.getContent());
    }

    @Override
    public int getItemCount() {
        return posts.size();
    }
}
```

```typescript
// HarmonyOS 对应实现 (ArkTS)
class PostDataSource implements IDataSource {
  private posts: Post[] = []

  totalCount(): number {
    return this.posts.length
  }

  getData(index: number): Post {
    return this.posts[index]
  }

  registerDataChangeListener(listener: DataChangeListener): void { }
  unregisterDataChangeListener(listener: DataChangeListener): void { }
}

@Component
struct PostList {
  private dataSource: PostDataSource = new PostDataSource()

  build() {
    List() {
      LazyForEach(this.dataSource, (post: Post) => {
        ListItem() {
          PostItemView({ post: post })
        }
      })
    }
  }
}
```

---

## 二、重要桥接 API (P1 - 功能性)

### 2.1 网络请求 API

| Android API | HarmonyOS 对应 | 桥接难度 |
|------------|---------------|---------|
| `java.net.HttpURLConnection` | `@ohos.net.http` | 中 |
| `java.net.URL` | `@ohos.uri` | 低 |
| `java.net.Socket` | `@ohos.net.socket` | 中 |
| `javax.net.ssl.*` | OHOS TLS 支持 | 中 |

**OkHttp**: 纯 Java 库，可直接使用，无需桥接

**Retrofit**: 依赖 OkHttp，可直接使用

### 2.2 数据存储 API

| Android API | HarmonyOS 对应 | 桥接方案 |
|------------|---------------|---------|
| `SharedPreferences` | `@ohos.data.preferences` | 直接映射 |
| `SQLiteDatabase` | `@ohos.data.relationalStore` | SQL 兼容，接口不同 |
| `SQLiteOpenHelper` | `RdbOpenCallback` | 回调映射 |
| `Cursor` | `ResultSet` | 包装适配 |
| `ContentValues` | `ValuesBucket` | 转换工具 |

**SharedPreferences 映射**:

```java
// Android
SharedPreferences prefs = context.getSharedPreferences("config", MODE_PRIVATE);
prefs.edit().putString("token", "xxx").apply();
String token = prefs.getString("token", "");

// CRAFT 生成的桥接代码
public class SharedPreferencesAdapter implements SharedPreferences {
    private Preferences ohosPrefs;

    public SharedPreferencesAdapter(Context context, String name) {
        this.ohosPrefs = dataPreferences.getPreferences(context, name);
    }

    @Override
    public String getString(String key, String defValue) {
        return ohosPrefs.get(key, defValue);
    }

    @Override
    public Editor edit() {
        return new EditorAdapter(ohosPrefs);
    }
}
```

### 2.3 图片处理 API

| Android API | HarmonyOS 对应 | 说明 |
|------------|---------------|------|
| `android.graphics.Bitmap` | `@ohos.multimedia.image.PixelMap` | 核心图片类 |
| `BitmapFactory.decodeFile()` | `image.createPixelMap()` | 解码方式不同 |
| `BitmapFactory.decodeStream()` | `image.createPixelMap()` | 流解码 |
| `Bitmap.createBitmap()` | `image.createPixelMap()` | 创建空图 |
| `Bitmap.compress()` | `imagePacker.packing()` | 压缩编码 |
| `Canvas` | `@ohos.graphics.drawing` | 绘图 API |

**Bitmap 桥接核心方法**:

```java
public class BitmapAdapter {
    private PixelMap pixelMap;

    public static BitmapAdapter decodeFile(String path) {
        ImageSource source = ImageSource.create(path);
        PixelMap pixelMap = source.createPixelMap();
        return new BitmapAdapter(pixelMap);
    }

    public int getWidth() {
        return pixelMap.getImageInfo().size.width;
    }

    public int getHeight() {
        return pixelMap.getImageInfo().size.height;
    }

    public boolean compress(CompressFormat format, int quality, OutputStream out) {
        ImagePacker packer = ImagePacker.create();
        PackingOptions options = new PackingOptions();
        options.format = format == CompressFormat.JPEG ? "image/jpeg" : "image/png";
        options.quality = quality;
        packer.packing(pixelMap, out, options);
        return true;
    }
}
```

### 2.4 文件操作 API

| Android API | HarmonyOS 对应 | 说明 |
|------------|---------------|------|
| `java.io.File` | `@ohos.file.fs` | 文件操作 |
| `FileInputStream/OutputStream` | `fs.open() + fs.read/write` | 流操作 |
| `Environment.getExternalStorageDirectory()` | `context.filesDir` | 存储路径 |
| `context.getCacheDir()` | `context.cacheDir` | 缓存目录 |
| `context.getFilesDir()` | `context.filesDir` | 文件目录 |

---

## 三、多媒体 API (P1-P2)

### 3.1 图片加载库适配

**Glide 适配层需要桥接的接口**:

```java
// 需要实现的 Glide 兼容接口
public class GlideCompat {
    // 核心加载方法
    public RequestBuilder load(String url);
    public RequestBuilder load(int resourceId);
    public RequestBuilder load(Uri uri);
    public RequestBuilder load(File file);
    public RequestBuilder load(byte[] bytes);

    // 配置方法
    public RequestBuilder placeholder(int resourceId);
    public RequestBuilder error(int resourceId);
    public RequestBuilder override(int width, int height);
    public RequestBuilder centerCrop();
    public RequestBuilder fitCenter();
    public RequestBuilder circleCrop();

    // 目标
    public void into(ImageView view);  // 关键: 需要转换为 OHOS Image
}
```

### 3.2 视频播放 API

| Android API | HarmonyOS 对应 | 复杂度 |
|------------|---------------|-------|
| `MediaPlayer` | `@ohos.multimedia.media.AVPlayer` | 高 |
| `VideoView` | `Video` 组件 | 中 |
| `SurfaceView` | `XComponent` | 高 |
| `MediaController` | 自定义控制器 | 中 |

**MediaPlayer 状态机映射**:

```
Android MediaPlayer States        HarmonyOS AVPlayer States
─────────────────────────        ──────────────────────────
Idle                          →  idle
Initialized                   →  initialized
Preparing                     →  preparing
Prepared                      →  prepared
Started                       →  playing
Paused                        →  paused
Stopped                       →  stopped
PlaybackCompleted             →  completed
Error                         →  error
End                           →  released
```

### 3.3 相机 API (发帖拍照)

| Android API | HarmonyOS 对应 | 说明 |
|------------|---------------|------|
| `Camera2 API` 全套 | `@ohos.multimedia.camera` | 差异很大 |
| `CameraManager` | `cameraManager` | 设备管理 |
| `CameraDevice` | `CameraInput` | 相机输入 |
| `CaptureRequest` | `PhotoOutput` | 拍照配置 |
| `CameraCaptureSession` | `CaptureSession` | 会话管理 |
| `ImageReader` | `ImageReceiver` | 图像接收 |

**Camera2 桥接关键类**:

```java
// 需要创建的桥接类
public class Camera2Compat {
    // 相机管理
    class CameraManagerCompat {
        String[] getCameraIdList();
        CameraCharacteristicsCompat getCameraCharacteristics(String id);
        void openCamera(String id, StateCallback callback, Handler handler);
    }

    // 相机设备
    class CameraDeviceCompat {
        void createCaptureSession(List<Surface> outputs, StateCallback callback);
        CaptureRequestBuilder createCaptureRequest(int templateType);
    }

    // 捕获请求
    class CaptureRequestBuilderCompat {
        void addTarget(Surface surface);
        void set(CaptureRequest.Key key, Object value);
        CaptureRequest build();
    }
}
```

---

## 四、系统服务 API (P1)

### 4.1 通知 API

| Android API | HarmonyOS 对应 | 说明 |
|------------|---------------|------|
| `NotificationManager` | `@ohos.notificationManager` | 通知管理 |
| `Notification.Builder` | `NotificationRequest` | 构建器模式不同 |
| `NotificationChannel` | `NotificationSlot` | 渠道/槽位 |
| `PendingIntent` | `WantAgent` | 延迟意图 |

**通知桥接示例**:

```java
// Android 原始代码
NotificationManager manager = getSystemService(NotificationManager.class);
Notification notification = new Notification.Builder(this, "channel_id")
    .setContentTitle("新回复")
    .setContentText("有人回复了你的帖子")
    .setSmallIcon(R.drawable.ic_notification)
    .setContentIntent(pendingIntent)
    .build();
manager.notify(1, notification);

// CRAFT 生成的桥接代码
public class NotificationManagerAdapter {
    private notificationManager ohosManager;

    public void notify(int id, Notification notification) {
        NotificationRequest request = convertToOHOS(notification);
        ohosManager.publish(request);
    }

    private NotificationRequest convertToOHOS(Notification android) {
        NotificationRequest request = new NotificationRequest();
        NotificationContent content = new NotificationContent();
        content.contentType = ContentType.NOTIFICATION_CONTENT_BASIC_TEXT;
        content.normal = new NotificationBasicContent();
        content.normal.title = android.extras.getString("title");
        content.normal.text = android.extras.getString("text");
        request.content = content;

        if (android.contentIntent != null) {
            request.wantAgent = PendingIntentConverter.toWantAgent(android.contentIntent);
        }

        return request;
    }
}
```

### 4.2 权限 API

| Android API | HarmonyOS 对应 | 说明 |
|------------|---------------|------|
| `checkSelfPermission()` | `abilityAccessCtrl.checkAccessToken()` | 权限检查 |
| `requestPermissions()` | `requestPermissionsFromUser()` | 请求权限 |
| `onRequestPermissionsResult()` | `Promise` 回调 | 结果处理 |

**权限映射表**:

```
Android Permission                    HarmonyOS Permission
────────────────────────────────     ────────────────────────────────
CAMERA                           →   ohos.permission.CAMERA
READ_EXTERNAL_STORAGE            →   ohos.permission.READ_MEDIA
WRITE_EXTERNAL_STORAGE           →   ohos.permission.WRITE_MEDIA
ACCESS_FINE_LOCATION             →   ohos.permission.APPROXIMATELY_LOCATION
ACCESS_COARSE_LOCATION           →   ohos.permission.LOCATION
RECORD_AUDIO                     →   ohos.permission.MICROPHONE
READ_CONTACTS                    →   ohos.permission.READ_CONTACTS
INTERNET                         →   ohos.permission.INTERNET
```

### 4.3 后台服务 API

| Android API | HarmonyOS 对应 | 说明 |
|------------|---------------|------|
| `Service` | `ServiceExtensionAbility` | 后台服务 |
| `IntentService` | `ServiceExtensionAbility` | 单次任务 |
| `JobScheduler` | `@ohos.resourceschedule.workScheduler` | 任务调度 |
| `AlarmManager` | `reminderAgentManager` | 定时任务 |
| `Handler/Looper` | `@ohos.taskpool` | 线程通信 |

---

## 五、WebView API (P1)

### 5.1 WebView 核心 API

| Android API | HarmonyOS 对应 | 复杂度 |
|------------|---------------|-------|
| `WebView` | `Web` 组件 | 高 |
| `WebViewClient` | `onPageBegin/onPageEnd` | 中 |
| `WebChromeClient` | `onConsole/onAlert` | 中 |
| `WebSettings` | `WebAttribute` | 中 |
| `JavascriptInterface` | `javaScriptProxy` | 高 |
| `evaluateJavascript()` | `runJavaScript()` | 中 |

**JS Bridge 桥接关键点**:

```java
// Android JS Bridge
public class JSBridge {
    @JavascriptInterface
    public void showToast(String message) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show();
    }

    @JavascriptInterface
    public String getToken() {
        return UserManager.getToken();
    }
}
webView.addJavascriptInterface(new JSBridge(), "NativeBridge");

// JavaScript 调用
NativeBridge.showToast("Hello");
var token = NativeBridge.getToken();
```

```typescript
// HarmonyOS 对应实现
@Component
struct WebContainer {
  controller: WebviewController = new webview.WebviewController()

  build() {
    Web({ src: 'https://tieba.baidu.com', controller: this.controller })
      .javaScriptProxy({
        object: this.createJSBridge(),
        name: "NativeBridge",
        methodList: ["showToast", "getToken"],
        controller: this.controller
      })
  }

  createJSBridge() {
    return {
      showToast: (message: string) => {
        promptAction.showToast({ message: message })
      },
      getToken: () => {
        return UserManager.getToken()
      }
    }
  }
}
```

---

## 六、第三方 SDK 处理策略

### 6.1 可直接使用的库

| 库名 | 版本 | 说明 |
|-----|------|------|
| Gson | 2.10+ | 纯 Java JSON 库 |
| OkHttp | 4.x | HTTP 客户端 |
| Retrofit | 2.x | REST 客户端 |
| RxJava | 3.x | 响应式编程 |
| Kotlin Coroutines | 1.x | 协程 |

### 6.2 需要适配层的库

| 库名 | 适配策略 | 工作量 |
|-----|---------|-------|
| Glide | 创建 ImageViewTarget 适配 | 中 |
| Fresco | 创建 DraweeView 适配 | 高 |
| Lottie | 使用 OHOS 动画替代 | 高 |
| EventBus | 纯 Java，可直接使用 | 无 |

### 6.3 需要替代方案的库

| 库名 | HarmonyOS 替代 | 说明 |
|-----|--------------|------|
| ExoPlayer | `AVPlayer` | 官方播放器 |
| CameraX | `Camera Kit` | 官方相机 |
| WorkManager | `workScheduler` | 任务调度 |
| Firebase | 华为 Push/Analytics | 厂商服务 |

### 6.4 需要厂商支持的 SDK

| SDK | 状态 | 解决方案 |
|-----|------|---------|
| 百度账号 SDK | ❌ 无 OHOS 版 | 推动百度适配 |
| 微信 SDK | ❌ 无 OHOS 版 | 推动腾讯适配 |
| 支付宝 SDK | ✅ 已有 | 直接使用 |
| 华为 HMS | ✅ 原生 | 直接使用 |

---

## 七、优先级排序总结

### P0 - 阻塞性 (第一阶段)
1. Activity/UIAbility 生命周期
2. Intent/Want 通信
3. 基础 View 组件
4. RecyclerView/List
5. SharedPreferences

### P1 - 核心功能 (第二阶段)
1. SQLite 数据库
2. 网络请求 (HTTP)
3. 图片加载 (Bitmap/PixelMap)
4. 通知系统
5. 权限管理

### P2 - 完整体验 (第三阶段)
1. 相机 API
2. 视频播放
3. WebView/JS Bridge
4. 后台服务
5. 推送通知

### P3 - 优化增强 (第四阶段)
1. 动画系统
2. 手势识别
3. 深度链接
4. Widget 小组件

---

## 八、工作量估算

| 模块 | API 数量 | CRAFT 自动化 | 人工审核 | 预计人天 |
|-----|---------|------------|---------|---------|
| 生命周期 | 20 | 60% | 8 | 2 |
| 基础 UI | 100 | 75% | 25 | 5 |
| 列表组件 | 30 | 50% | 15 | 4 |
| 数据存储 | 40 | 80% | 8 | 2 |
| 网络 | 30 | 85% | 5 | 1 |
| 图片 | 50 | 60% | 20 | 4 |
| 多媒体 | 60 | 40% | 36 | 8 |
| 系统服务 | 50 | 55% | 23 | 5 |
| WebView | 30 | 40% | 18 | 5 |
| **合计** | **410** | **~62%** | **~158** | **~36** |

**结论**: 使用 CRAFT 自动化后，百度贴吧适配预计需要 **36 人天** 的人工审核和深度桥接工作，相比纯人工的 70+ 人天节省约 50%。

---

*文档版本: 1.0.0*
*更新日期: 2026-01-18*
