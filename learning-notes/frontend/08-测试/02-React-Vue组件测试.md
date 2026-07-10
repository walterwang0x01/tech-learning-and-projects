# React / Vue 组件测试
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. React Testing Library

<!-- version-check: @testing-library/react 16.3.2, @vue/test-utils 2.4.11, checked 2026-07-10 -->

```jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest'; // 或 jest（API 兼容）
import Counter from './Counter';

describe('Counter', () => {
  it('renders initial count', () => {
    render(<Counter initialCount={0} />);
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
  });

  it('increments on click', async () => {
    const user = userEvent.setup();
    render(<Counter initialCount={0} />);

    await user.click(screen.getByRole('button', { name: '+1' }));
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText('用户名'), 'zhangsan');
    await user.type(screen.getByLabelText('密码'), '123456');
    await user.click(screen.getByRole('button', { name: '登录' }));

    expect(onSubmit).toHaveBeenCalledWith({
      username: 'zhangsan',
      password: '123456',
    });
  });

  it('fetches and displays data', async () => {
    render(<UserList />);

    // 等待异步数据加载
    await waitFor(() => {
      expect(screen.getByText('张三')).toBeInTheDocument();
    });
  });
});

// 查询优先级（推荐顺序）：
// 1. getByRole       — 按角色查询（最推荐）
// 2. getByLabelText  — 按标签文本
// 3. getByPlaceholderText
// 4. getByText       — 按文本内容
// 5. getByTestId     — 按 data-testid（最后手段）
```

## 2. Vue Test Utils

```javascript
import { mount, shallowMount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import Counter from './Counter.vue';

describe('Counter', () => {
  it('renders count', () => {
    const wrapper = mount(Counter, {
      props: { initialCount: 5 },
    });
    expect(wrapper.text()).toContain('5');
  });

  it('increments on click', async () => {
    const wrapper = mount(Counter);
    await wrapper.find('button').trigger('click');
    expect(wrapper.text()).toContain('1');
  });

  it('emits update event', async () => {
    const wrapper = mount(Counter);
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('update')).toHaveLength(1);
    expect(wrapper.emitted('update')[0]).toEqual([1]);
  });

  it('with Pinia store', () => {
    const wrapper = mount(Counter, {
      global: {
        plugins: [createTestingPinia({ initialState: { counter: { count: 10 } } })],
      },
    });
    expect(wrapper.text()).toContain('10');
  });
});
```

## 3. Hook 测试

```javascript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('should increment', () => {
    const { result } = renderHook(() => useCounter(0));

    act(() => { result.current.increment(); });

    expect(result.current.count).toBe(1);
  });
});
```
