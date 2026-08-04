# 自定义 View 与绘制
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Canvas 与 Paint

```kotlin
class ChartView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val linePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        strokeWidth = 4f
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }

    private val fillPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        shader = LinearGradient(0f, 0f, 0f, 300f,
            Color.parseColor("#4488FF"), Color.TRANSPARENT, Shader.TileMode.CLAMP)
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.GRAY
        textSize = 32f
        textAlign = Paint.Align.CENTER
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // 绘制基本图形
        canvas.drawLine(0f, 0f, width.toFloat(), height.toFloat(), linePaint)
        canvas.drawCircle(width / 2f, height / 2f, 100f, fillPaint)
        canvas.drawRoundRect(20f, 20f, 200f, 100f, 16f, 16f, linePaint)
        canvas.drawText("标签", width / 2f, height - 20f, textPaint)
    }
}
```

## 2. Path 绘制

```kotlin
class WaveView(context: Context, attrs: AttributeSet?) : View(context, attrs) {
    private val path = Path()
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#2196F3")
        style = Paint.Style.FILL
    }

    override fun onDraw(canvas: Canvas) {
        val w = width.toFloat()
        val h = height.toFloat()
        path.reset()
        path.moveTo(0f, h * 0.5f)
        path.quadTo(w * 0.25f, h * 0.3f, w * 0.5f, h * 0.5f)
        path.quadTo(w * 0.75f, h * 0.7f, w, h * 0.5f)
        path.lineTo(w, h)
        path.lineTo(0f, h)
        path.close()
        canvas.drawPath(path, paint)
    }
}
```

## 3. 自定义属性

```xml
<!-- res/values/attrs.xml -->
<declare-styleable name="ProgressRing">
    <attr name="ringColor" format="color" />
    <attr name="ringWidth" format="dimension" />
    <attr name="progress" format="integer" />
</declare-styleable>
```

```kotlin
class ProgressRing @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var ringColor = Color.BLUE
    private var ringWidth = 12f
    var progress: Int = 0
        set(value) { field = value.coerceIn(0, 100); invalidate() }

    init {
        context.obtainStyledAttributes(attrs, R.styleable.ProgressRing).use { ta ->
            ringColor = ta.getColor(R.styleable.ProgressRing_ringColor, Color.BLUE)
            ringWidth = ta.getDimension(R.styleable.ProgressRing_ringWidth, 12f)
            progress = ta.getInt(R.styleable.ProgressRing_progress, 0)
        }
    }

    private val bgPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE; strokeWidth = ringWidth; color = Color.LTGRAY
    }
    private val fgPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE; strokeWidth = ringWidth; color = ringColor
        strokeCap = Paint.Cap.ROUND
    }

    override fun onDraw(canvas: Canvas) {
        val cx = width / 2f; val cy = height / 2f
        val radius = min(cx, cy) - ringWidth
        canvas.drawCircle(cx, cy, radius, bgPaint)
        val sweepAngle = 360f * progress / 100f
        val rect = RectF(cx - radius, cy - radius, cx + radius, cy + radius)
        canvas.drawArc(rect, -90f, sweepAngle, false, fgPaint)
    }
}
```

## 4. onMeasure 自定义测量

```kotlin
class SquareImageView(context: Context, attrs: AttributeSet?) : AppCompatImageView(context, attrs) {
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
        val size = min(measuredWidth, measuredHeight)
        setMeasuredDimension(size, size)  // 强制正方形
    }
}
```

## 5. 属性动画驱动绘制

```kotlin
class PulseView(context: Context, attrs: AttributeSet?) : View(context, attrs) {
    private var radius = 0f
    private var alpha = 255

    private val animator = ValueAnimator.ofFloat(0f, 1f).apply {
        duration = 1500
        repeatCount = ValueAnimator.INFINITE
        interpolator = AccelerateDecelerateInterpolator()
        addUpdateListener {
            val fraction = it.animatedValue as Float
            radius = width / 2f * fraction
            alpha = (255 * (1 - fraction)).toInt()
            invalidate()
        }
    }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.RED }

    override fun onDraw(canvas: Canvas) {
        paint.alpha = alpha
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }

    override fun onAttachedToWindow() { super.onAttachedToWindow(); animator.start() }
    override fun onDetachedFromWindow() { animator.cancel(); super.onDetachedFromWindow() }
}
```
