# View 与 ViewGroup 基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. View 绘制流程

```kotlin
// 三大流程: measure → layout → draw
class CustomView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    // 1. 测量：确定 View 大小
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val width = when (widthMode) {
            MeasureSpec.EXACTLY -> widthSize          // match_parent / 固定值
            MeasureSpec.AT_MOST -> min(desiredWidth, widthSize)  // wrap_content
            else -> desiredWidth                       // UNSPECIFIED
        }
        setMeasuredDimension(width, height)
    }

    // 2. 布局：确定 View 位置（ViewGroup 中重写）
    // override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int)

    // 3. 绘制
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    }
}
```

## 2. 事件分发机制

```kotlin
// 事件分发三个关键方法
// dispatchTouchEvent → onInterceptTouchEvent → onTouchEvent

// 自定义 ViewGroup 拦截事件
class SwipeLayout(context: Context, attrs: AttributeSet?) : FrameLayout(context, attrs) {
    private var startX = 0f

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        return when (ev.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = ev.x
                false  // 不拦截 DOWN
            }
            MotionEvent.ACTION_MOVE -> {
                abs(ev.x - startX) > ViewConfiguration.get(context).scaledTouchSlop
            }
            else -> false
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_MOVE -> { /* 处理滑动 */ }
            MotionEvent.ACTION_UP -> { /* 处理抬起 */ }
        }
        return true
    }
}
```

## 3. 常用布局

```kotlin
// LinearLayout
<LinearLayout
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="wrap_content">
    <TextView android:layout_weight="1" ... />
    <Button android:layout_weight="0" ... />
</LinearLayout>

// FrameLayout（层叠）
<FrameLayout ...>
    <ImageView android:layout_gravity="center" ... />
    <TextView android:layout_gravity="bottom|center_horizontal" ... />
</FrameLayout>
```

## 4. ViewBinding

```kotlin
// build.gradle.kts
// buildFeatures { viewBinding = true }

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.tvTitle.text = "Hello"
        binding.btnSubmit.setOnClickListener { submit() }
    }
}

// Fragment 中使用
class HomeFragment : Fragment(R.layout.fragment_home) {
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        _binding = FragmentHomeBinding.bind(view)
        binding.recyclerView.adapter = adapter
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // 避免内存泄漏
    }
}
```
