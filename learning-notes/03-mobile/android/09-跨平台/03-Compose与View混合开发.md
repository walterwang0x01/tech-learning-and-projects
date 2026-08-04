# Compose 与 View 混合开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ComposeView 嵌入 XML 布局

```xml
<!-- res/layout/activity_main.xml -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:id="@+id/tvTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="传统 View 标题" />

    <androidx.compose.ui.platform.ComposeView
        android:id="@+id/composeView"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<ComposeView>(R.id.composeView).apply {
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)
            setContent {
                MyTheme {
                    UserListCompose(viewModel = viewModel())
                }
            }
        }
    }
}
```

## 2. Fragment 中使用 ComposeView

```kotlin
class HomeFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)
            setContent {
                MyTheme {
                    HomeScreen(viewModel = hiltViewModel())
                }
            }
        }
    }
}
```

## 3. AndroidView 嵌入 Compose

```kotlin
// 在 Compose 中使用传统 View
@Composable
fun MapViewCompose(location: LatLng) {
    AndroidView(
        factory = { context ->
            MapView(context).apply {
                onCreate(null)
                getMapAsync { map ->
                    map.moveCamera(CameraUpdateFactory.newLatLngZoom(location, 15f))
                }
            }
        },
        update = { mapView ->
            mapView.getMapAsync { map ->
                map.clear()
                map.addMarker(MarkerOptions().position(location))
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}

// 嵌入 WebView
@Composable
fun WebViewCompose(url: String) {
    AndroidView(
        factory = { context ->
            WebView(context).apply {
                settings.javaScriptEnabled = true
                webViewClient = WebViewClient()
                loadUrl(url)
            }
        },
        update = { it.loadUrl(url) },
        modifier = Modifier.fillMaxSize()
    )
}

// 嵌入 AdView
@Composable
fun BannerAd(adUnitId: String) {
    AndroidView(
        factory = { context ->
            AdView(context).apply {
                setAdSize(AdSize.BANNER)
                this.adUnitId = adUnitId
                loadAd(AdRequest.Builder().build())
            }
        }
    )
}
```

## 4. ViewCompositionStrategy

```kotlin
// 控制 Compose 组合的生命周期
composeView.setViewCompositionStrategy(
    // Fragment 中推荐：随 ViewLifecycleOwner 销毁
    ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed

    // Activity 中：随 Window detach 销毁（默认）
    // ViewCompositionStrategy.DisposeOnDetachedFromWindow

    // RecyclerView 中：随 ViewTreeLifecycleOwner 销毁
    // ViewCompositionStrategy.DisposeOnDetachedFromWindowOrReleasedFromPool
)
```

## 5. 主题互通

```kotlin
// 在 Compose 中使用 XML 主题
@Composable
fun MdcThemeBridge(content: @Composable () -> Unit) {
    // 依赖: com.google.accompanist:accompanist-themeadapter-material3
    Mdc3Theme {
        content()
    }
}

// 在 Compose 中读取 XML 属性
@Composable
fun ThemedText() {
    val context = LocalContext.current
    val typedValue = TypedValue()
    context.theme.resolveAttribute(com.google.android.material.R.attr.colorPrimary, typedValue, true)
    val primaryColor = Color(typedValue.data)

    Text("主题色文字", color = primaryColor)
}
```
