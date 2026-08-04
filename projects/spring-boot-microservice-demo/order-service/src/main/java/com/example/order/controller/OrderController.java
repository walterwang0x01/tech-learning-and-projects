package com.example.order.controller;

import com.example.common.response.ApiResponse;
import com.example.order.dto.OrderCreateRequest;
import com.example.order.dto.OrderResponse;
import com.example.order.entity.Order;
import com.example.order.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 订单服务控制器
 */
@Tag(name = "订单管理", description = "订单服务的 CRUD 操作和状态管理")
@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @Operation(summary = "创建订单", description = "创建新订单并发送订单创建事件到 Kafka")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "201", description = "订单创建成功"),
            @ApiResponse(responseCode = "400", description = "参数验证失败")
    })
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ApiResponse<OrderResponse> createOrder(
            @Parameter(description = "订单创建请求", required = true)
            @Valid @RequestBody OrderCreateRequest request) {
        OrderResponse order = orderService.createOrder(request);
        return ApiResponse.success("订单创建成功", order);
    }

    @Operation(summary = "获取订单", description = "根据订单ID获取订单信息")
    @GetMapping("/{id}")
    public ApiResponse<OrderResponse> getOrderById(
            @Parameter(description = "订单ID", required = true)
            @PathVariable Long id) {
        OrderResponse order = orderService.getOrderById(id);
        return ApiResponse.success(order);
    }

    @Operation(summary = "根据订单号获取订单", description = "根据订单号查询订单")
    @GetMapping("/number/{orderNumber}")
    public ApiResponse<OrderResponse> getOrderByOrderNumber(
            @Parameter(description = "订单号", required = true)
            @PathVariable String orderNumber) {
        OrderResponse order = orderService.getOrderByOrderNumber(orderNumber);
        return ApiResponse.success(order);
    }

    @Operation(summary = "获取客户订单列表", description = "根据客户ID获取订单列表")
    @GetMapping("/customer/{customerId}")
    public ApiResponse<List<OrderResponse>> getOrdersByCustomerId(
            @Parameter(description = "客户ID", required = true)
            @PathVariable Long customerId) {
        List<OrderResponse> orders = orderService.getOrdersByCustomerId(customerId);
        return ApiResponse.success(orders);
    }

    @Operation(summary = "更新订单状态", description = "更新订单状态并发送状态更新事件")
    @PutMapping("/{id}/status")
    public ApiResponse<OrderResponse> updateOrderStatus(
            @Parameter(description = "订单ID", required = true)
            @PathVariable Long id,
            @Parameter(description = "新状态", required = true)
            @RequestParam Order.OrderStatus status) {
        OrderResponse order = orderService.updateOrderStatus(id, status);
        return ApiResponse.success("订单状态更新成功", order);
    }
}

