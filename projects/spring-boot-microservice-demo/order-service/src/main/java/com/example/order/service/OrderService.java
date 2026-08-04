package com.example.order.service;

import com.example.common.exception.BusinessException;
import com.example.order.dto.OrderCreateRequest;
import com.example.order.dto.OrderItemRequest;
import com.example.order.dto.OrderResponse;
import com.example.order.entity.Order;
import com.example.order.entity.OrderItem;
import com.example.order.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * 订单服务
 * 演示事件驱动架构：监听用户创建事件，发布订单创建事件
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Transactional
    public OrderResponse createOrder(OrderCreateRequest request) {
        // 生成订单号
        String orderNumber = generateOrderNumber();

        // 计算总金额
        BigDecimal totalAmount = request.getItems().stream()
                .map(item -> item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        // 创建订单
        Order order = Order.builder()
                .orderNumber(orderNumber)
                .customerId(request.getCustomerId())
                .status(Order.OrderStatus.PENDING)
                .totalAmount(totalAmount)
                .build();

        // 创建订单项
        List<OrderItem> items = request.getItems().stream()
                .map(itemRequest -> {
                    BigDecimal subtotal = itemRequest.getPrice()
                            .multiply(BigDecimal.valueOf(itemRequest.getQuantity()));
                    return OrderItem.builder()
                            .order(order)
                            .productId(itemRequest.getProductId())
                            .quantity(itemRequest.getQuantity())
                            .price(itemRequest.getPrice())
                            .subtotal(subtotal)
                            .build();
                })
                .collect(Collectors.toList());

        order.setItems(items);
        order = orderRepository.save(order);

        log.info("订单创建成功: orderId={}, orderNumber={}, customerId={}, totalAmount={}",
                order.getId(), orderNumber, request.getCustomerId(), totalAmount);

        // 发送订单创建事件到 Kafka
        kafkaTemplate.send("order-created", order.getId().toString(), order);

        return mapToResponse(order);
    }

    public OrderResponse getOrderById(Long id) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new BusinessException("订单不存在"));
        return mapToResponse(order);
    }

    public OrderResponse getOrderByOrderNumber(String orderNumber) {
        Order order = orderRepository.findByOrderNumber(orderNumber)
                .orElseThrow(() -> new BusinessException("订单不存在"));
        return mapToResponse(order);
    }

    public List<OrderResponse> getOrdersByCustomerId(Long customerId) {
        return orderRepository.findByCustomerId(customerId).stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Transactional
    public OrderResponse updateOrderStatus(Long id, Order.OrderStatus status) {
        Order order = orderRepository.findById(id)
                .orElseThrow(() -> new BusinessException("订单不存在"));

        order.setStatus(status);
        order = orderRepository.save(order);

        log.info("订单状态更新: orderId={}, newStatus={}", id, status);

        // 发送订单状态更新事件
        kafkaTemplate.send("order-status-updated", order.getId().toString(), order);

        return mapToResponse(order);
    }

    private String generateOrderNumber() {
        return "ORD-" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    private OrderResponse mapToResponse(Order order) {
        return OrderResponse.builder()
                .id(order.getId())
                .orderNumber(order.getOrderNumber())
                .customerId(order.getCustomerId())
                .status(order.getStatus())
                .totalAmount(order.getTotalAmount())
                .items(order.getItems().stream()
                        .map(item -> com.example.order.dto.OrderItemResponse.builder()
                                .id(item.getId())
                                .productId(item.getProductId())
                                .quantity(item.getQuantity())
                                .price(item.getPrice())
                                .subtotal(item.getSubtotal())
                                .build())
                        .collect(Collectors.toList()))
                .createdAt(order.getCreatedAt())
                .updatedAt(order.getUpdatedAt())
                .build();
    }
}

