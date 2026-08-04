# JavaScript 数据类型与变量
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 数据类型

### 1.1 基本类型（原始类型）

```javascript
// 7种基本类型
let str = 'hello';        // String
let num = 42;             // Number（包括整数和浮点数）
let big = 9007199254740991n; // BigInt
let bool = true;          // Boolean
let undef = undefined;    // Undefined
let nul = null;           // Null
let sym = Symbol('id');   // Symbol
```

### 1.2 引用类型

```javascript
let obj = { name: '张三' };  // Object
let arr = [1, 2, 3];         // Array（本质是Object）
let fn = function() {};       // Function（本质是Object）
let date = new Date();        // Date
let reg = /pattern/g;         // RegExp
let map = new Map();          // Map
let set = new Set();          // Set
```

### 1.3 基本类型 vs 引用类型

```javascript
// 基本类型：值存储在栈中，赋值是值拷贝
let a = 10;
let b = a;
b = 20;
console.log(a); // 10（不受影响）

// 引用类型：值存储在堆中，变量保存引用地址
let obj1 = { name: '张三' };
let obj2 = obj1;
obj2.name = '李四';
console.log(obj1.name); // '李四'（被修改了）
```

## 2. 类型判断

```javascript
// typeof（适合基本类型，对象类型不精确）
typeof 'hello'     // 'string'
typeof 42          // 'number'
typeof true        // 'boolean'
typeof undefined   // 'undefined'
typeof null        // 'object'  ⚠️ 历史遗留bug
typeof {}          // 'object'
typeof []          // 'object'  ⚠️ 无法区分数组
typeof function(){} // 'function'
typeof Symbol()    // 'symbol'

// instanceof（检查原型链，适合引用类型）
[] instanceof Array   // true
{} instanceof Object  // true
/a/ instanceof RegExp // true

// Object.prototype.toString（最准确）
Object.prototype.toString.call('hello')    // '[object String]'
Object.prototype.toString.call(42)         // '[object Number]'
Object.prototype.toString.call(null)       // '[object Null]'
Object.prototype.toString.call([])         // '[object Array]'
Object.prototype.toString.call({})         // '[object Object]'
Object.prototype.toString.call(new Date()) // '[object Date]'

// Array.isArray（判断数组）
Array.isArray([1, 2, 3]) // true
Array.isArray('hello')   // false
```

## 3. 类型转换

### 3.1 隐式转换

```javascript
// 字符串拼接
'5' + 3       // '53'（数字转字符串）
'5' - 3       // 2（字符串转数字）
'5' * '2'     // 10

// 布尔转换（假值：false, 0, '', null, undefined, NaN）
Boolean(0)         // false
Boolean('')        // false
Boolean(null)      // false
Boolean(undefined) // false
Boolean(NaN)       // false
Boolean([])        // true  ⚠️ 空数组是真值
Boolean({})        // true  ⚠️ 空对象是真值

// == 的隐式转换（不推荐使用 ==）
null == undefined  // true
null == 0          // false
'' == 0            // true
'0' == false       // true
```

### 3.2 显式转换

```javascript
// 转数字
Number('123')     // 123
Number('abc')     // NaN
Number(true)      // 1
parseInt('123px') // 123
parseFloat('3.14') // 3.14

// 转字符串
String(123)       // '123'
(123).toString()  // '123'
123 + ''          // '123'

// 转布尔
Boolean(1)        // true
!!1               // true（双重取反）
```

## 4. 变量声明

### 4.1 var / let / const

```javascript
// var：函数作用域，存在变量提升
console.log(a); // undefined（变量提升）
var a = 10;

// let：块级作用域，不存在变量提升（暂时性死区）
// console.log(b); // ReferenceError
let b = 20;

// const：块级作用域，声明时必须赋值，不可重新赋值
const c = 30;
// c = 40; // TypeError

// const 对象的属性可以修改
const obj = { name: '张三' };
obj.name = '李四'; // 可以
// obj = {};       // TypeError
```

### 4.2 暂时性死区（TDZ）

```javascript
let x = 10;
{
  // console.log(x); // ReferenceError（TDZ）
  let x = 20; // 块级作用域内的 x
  console.log(x); // 20
}
console.log(x); // 10
```

## 5. 深拷贝与浅拷贝

```javascript
// 浅拷贝
const shallow1 = Object.assign({}, original);
const shallow2 = { ...original };
const shallow3 = Array.from(originalArr);
const shallow4 = [...originalArr];

// 深拷贝
// 方法1：structuredClone（推荐，现代浏览器）
const deep1 = structuredClone(original);

// 方法2：JSON（不支持函数、undefined、Symbol、循环引用）
const deep2 = JSON.parse(JSON.stringify(original));

// 方法3：手写递归
function deepClone(obj, map = new WeakMap()) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (map.has(obj)) return map.get(obj); // 处理循环引用

  const clone = Array.isArray(obj) ? [] : {};
  map.set(obj, clone);

  for (const key of Object.keys(obj)) {
    clone[key] = deepClone(obj[key], map);
  }
  return clone;
}
```
