package com.example.order.config;

import com.example.user.entity.User;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka 消费者配置
 * 演示事件驱动架构：监听用户创建事件
 */
@Slf4j
@Component
public class KafkaConsumerConfig {

    /**
     * 监听用户创建事件
     * 当用户创建时，可以执行相关业务逻辑（如创建默认订单、发送欢迎消息等）
     */
    @KafkaListener(topics = "user-created", groupId = "order-service-group")
    public void handleUserCreated(User user) {
        log.info("收到用户创建事件: userId={}, email={}", user.getId(), user.getEmail());
        
        // 可以在这里执行相关业务逻辑
        // 例如：为新用户创建欢迎订单、初始化用户数据等
    }
}

