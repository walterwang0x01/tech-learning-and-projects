package com.example.common.logging;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

/**
 * TraceId 过滤器
 * 为每个请求生成唯一的 TraceId，用于全链路追踪
 */
@Slf4j
@Component
@Order(1)
public class TraceIdFilter extends OncePerRequestFilter {

    private static final String TRACE_ID_HEADER = "X-Trace-Id";
    private static final String TRACE_ID_MDC_KEY = "traceId";

    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                   HttpServletResponse response, 
                                   FilterChain filterChain) 
            throws ServletException, IOException {
        try {
            // 从请求头获取 TraceId，如果没有则生成新的
            String traceId = request.getHeader(TRACE_ID_HEADER);
            if (traceId == null || traceId.isEmpty()) {
                traceId = UUID.randomUUID().toString().replace("-", "");
            }

            // 设置到 MDC 中，供日志使用
            MDC.put(TRACE_ID_MDC_KEY, traceId);
            
            // 将 TraceId 添加到响应头
            response.setHeader(TRACE_ID_HEADER, traceId);

            log.debug("Request TraceId: {}", traceId);
            filterChain.doFilter(request, response);
        } finally {
            // 清除 MDC，避免内存泄漏
            MDC.clear();
        }
    }
}

