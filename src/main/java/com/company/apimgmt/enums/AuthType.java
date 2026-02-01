package com.company.apimgmt.enums;

/**
 * 认证类型枚举
 * 支持的API认证方式
 */
public enum AuthType {
    API_KEY,
    OAUTH2,
    BASIC_AUTH,
    JWT,
    NONE
}
