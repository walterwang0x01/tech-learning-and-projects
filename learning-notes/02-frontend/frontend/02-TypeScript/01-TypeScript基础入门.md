# TypeScript 基础入门
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基础类型

```typescript
// 基本类型
let str: string = 'hello';
let num: number = 42;
let bool: boolean = true;
let n: null = null;
let u: undefined = undefined;

// 数组
let arr: number[] = [1, 2, 3];
let arr2: Array<string> = ['a', 'b'];

// 元组
let tuple: [string, number] = ['张三', 25];

// 枚举
enum Status { Active = 1, Inactive, Deleted }
const s: Status = Status.Active; // 1

// any / unknown / never / void
let a: any = 'anything';       // 跳过类型检查（不推荐）
let b: unknown = 'unknown';    // 安全的 any，使用前需类型检查
function fail(): never { throw new Error('error'); } // 永不返回
function log(): void { console.log('no return'); }   // 无返回值
```

## 2. 接口与类型别名

```typescript
// interface（可扩展、可合并）
interface User {
  id: number;
  name: string;
  age?: number;              // 可选属性
  readonly email: string;    // 只读属性
  greet(): string;           // 方法
}

// 接口继承
interface Admin extends User {
  role: string;
  permissions: string[];
}

// 接口合并（同名接口自动合并）
interface User { phone: string; }

// type（类型别名，更灵活）
type ID = string | number;
type Point = { x: number; y: number };
type Callback = (data: string) => void;

// interface vs type
// interface：可继承、可合并、适合定义对象结构
// type：可定义联合类型、交叉类型、元组、更灵活
```

## 3. 联合类型与交叉类型

```typescript
// 联合类型（或）
type StringOrNumber = string | number;
function format(value: string | number): string {
  if (typeof value === 'string') return value.toUpperCase();
  return value.toFixed(2);
}

// 交叉类型（且）
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged; // { name: string; age: number }

// 字面量类型
type Direction = 'up' | 'down' | 'left' | 'right';
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
```

## 4. 函数类型

```typescript
// 函数声明
function add(a: number, b: number): number { return a + b; }

// 箭头函数
const multiply = (a: number, b: number): number => a * b;

// 可选参数与默认值
function greet(name: string, greeting: string = 'Hello'): string {
  return `${greeting}, ${name}`;
}

// 剩余参数
function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}

// 函数重载
function parse(input: string): number;
function parse(input: number): string;
function parse(input: string | number): string | number {
  if (typeof input === 'string') return parseInt(input);
  return input.toString();
}
```

## 5. 类

```typescript
class Animal {
  // 访问修饰符
  public name: string;       // 公开（默认）
  protected type: string;    // 受保护（子类可访问）
  private _age: number;      // 私有
  readonly id: number;       // 只读

  constructor(name: string, age: number) {
    this.name = name;
    this._age = age;
    this.type = 'animal';
    this.id = Math.random();
  }

  // getter / setter
  get age(): number { return this._age; }
  set age(val: number) {
    if (val < 0) throw new Error('Age must be positive');
    this._age = val;
  }

  // 静态方法
  static create(name: string): Animal {
    return new Animal(name, 0);
  }
}

// 抽象类（不能实例化，只能被继承）
abstract class Shape {
  abstract area(): number;
  describe(): string { return `Area: ${this.area()}`; }
}

class Circle extends Shape {
  constructor(private radius: number) { super(); }
  area(): number { return Math.PI * this.radius ** 2; }
}
```

## 6. 类型守卫

```typescript
// typeof
function process(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase(); // TypeScript 知道这里是 string
  }
  return value.toFixed(2);
}

// instanceof
function handle(err: Error | string) {
  if (err instanceof Error) {
    return err.message;
  }
  return err;
}

// in
interface Fish { swim(): void; }
interface Bird { fly(): void; }
function move(animal: Fish | Bird) {
  if ('swim' in animal) {
    animal.swim();
  } else {
    animal.fly();
  }
}

// 自定义类型守卫
function isString(value: unknown): value is string {
  return typeof value === 'string';
}
```

## 7. 类型断言

```typescript
// as 语法（推荐）
const input = document.getElementById('input') as HTMLInputElement;
input.value = 'hello';

// 非空断言
const el = document.getElementById('app')!; // 断言不为 null

// const 断言
const config = { url: '/api', method: 'GET' } as const;
// 类型变为 { readonly url: "/api"; readonly method: "GET" }
```
## 🎬 推荐视频资源

- [freeCodeCamp - TypeScript Full Course](https://www.youtube.com/watch?v=30LWjhZzg50) — TypeScript完整课程
- [Fireship - TypeScript in 100 Seconds](https://www.youtube.com/watch?v=zQnBQ4tB3ZA) — TypeScript快速了解
- [Matt Pocock - Total TypeScript](https://www.youtube.com/@maaboroshi) — TypeScript高级技巧
### 📺 B站（Bilibili）
- [黑马程序员 - TypeScript教程](https://www.bilibili.com/video/BV1YP411S7cC) — TS完整中文教程
- [尚硅谷 - TypeScript教程](https://www.bilibili.com/video/BV1Xy4y1v7S2) — TS深入讲解

### 🌐 其他平台
- [TypeScript官方中文文档](https://www.typescriptlang.org/zh/) — 官方中文文档
