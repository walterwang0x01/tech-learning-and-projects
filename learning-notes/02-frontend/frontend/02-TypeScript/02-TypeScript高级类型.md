# TypeScript 高级类型
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 泛型

```typescript
// 泛型函数
function identity<T>(value: T): T { return value; }
identity<string>('hello');
identity(42); // 类型推断

// 泛型接口
interface ApiResponse<T> {
  code: number;
  data: T;
  message: string;
}
const res: ApiResponse<User[]> = await fetchUsers();

// 泛型类
class Stack<T> {
  private items: T[] = [];
  push(item: T): void { this.items.push(item); }
  pop(): T | undefined { return this.items.pop(); }
}

// 泛型约束
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// 多个泛型参数
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}
```

## 2. 条件类型

```typescript
// 基本语法：T extends U ? X : Y
type IsString<T> = T extends string ? true : false;
type A = IsString<string>;  // true
type B = IsString<number>;  // false

// 分布式条件类型（联合类型会分发）
type ToArray<T> = T extends any ? T[] : never;
type C = ToArray<string | number>; // string[] | number[]

// infer 关键字（提取类型）
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type UnpackPromise<T> = T extends Promise<infer U> ? U : T;
type ArrayElement<T> = T extends (infer E)[] ? E : T;

// 示例
type R = ReturnType<() => string>;        // string
type U = UnpackPromise<Promise<number>>;  // number
type E = ArrayElement<string[]>;          // string
```

## 3. 映射类型

```typescript
// 基本映射
type Readonly<T> = { readonly [K in keyof T]: T[K] };
type Optional<T> = { [K in keyof T]?: T[K] };
type Nullable<T> = { [K in keyof T]: T[K] | null };

// 键重映射（as）
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
// { getName: () => string; getAge: () => number; }

// 过滤键
type FilterByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};
type StringProps = FilterByType<User, string>; // 只保留 string 类型的属性
```

## 4. 内置工具类型

```typescript
// 属性修饰
Partial<T>       // 所有属性可选
Required<T>      // 所有属性必填
Readonly<T>      // 所有属性只读

// 属性选取
Pick<T, K>       // 选取指定属性
Omit<T, K>       // 排除指定属性
Record<K, V>     // 构造键值对类型

// 联合类型操作
Exclude<T, U>    // 从 T 中排除 U
Extract<T, U>    // 从 T 中提取 U
NonNullable<T>   // 排除 null 和 undefined

// 函数相关
ReturnType<T>    // 函数返回类型
Parameters<T>    // 函数参数类型（元组）
ConstructorParameters<T> // 构造函数参数类型

// 字符串操作
Uppercase<S>     // 转大写
Lowercase<S>     // 转小写
Capitalize<S>    // 首字母大写
Uncapitalize<S>  // 首字母小写

// 实际应用
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

type CreateUserDTO = Omit<User, 'id'>;
type UpdateUserDTO = Partial<Omit<User, 'id'>>;
type UserPreview = Pick<User, 'id' | 'name'>;
```

## 5. 模板字面量类型

```typescript
type EventName = `on${Capitalize<'click' | 'focus' | 'blur'>}`;
// 'onClick' | 'onFocus' | 'onBlur'

type CSSProperty = `${string}-${string}`;
type HTTPMethod = `${'GET' | 'POST' | 'PUT' | 'DELETE'}`;

// 实际应用：类型安全的事件系统
type EventMap = {
  click: { x: number; y: number };
  focus: { target: HTMLElement };
};

type EventHandler<T extends keyof EventMap> = (event: EventMap[T]) => void;
```

## 6. 类型体操示例

```typescript
// DeepReadonly
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// DeepPartial
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

// TupleToUnion
type TupleToUnion<T extends any[]> = T[number];
type U = TupleToUnion<[string, number, boolean]>; // string | number | boolean

// 获取对象值类型的联合
type ValueOf<T> = T[keyof T];
```
