package com.company.apimgmt.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.List;
import java.util.regex.Pattern;

public class EmailListValidator implements ConstraintValidator<ValidEmailList, List<String>> {
    
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
    );
    
    private int maxEmails;
    
    @Override
    public void initialize(ValidEmailList constraintAnnotation) {
        this.maxEmails = constraintAnnotation.max();
    }
    
    @Override
    public boolean isValid(List<String> emails, ConstraintValidatorContext context) {
        if (emails == null) {
            return true; // Use @NotNull for null checks
        }
        
        // Check max size
        if (emails.size() > maxEmails) {
            context.disableDefaultConstraintViolation();
            context.buildConstraintViolationWithTemplate(
                String.format("Email list cannot contain more than %d addresses", maxEmails)
            ).addConstraintViolation();
            return false;
        }
        
        // Validate each email
        for (String email : emails) {
            if (email == null || email.trim().isEmpty()) {
                context.disableDefaultConstraintViolation();
                context.buildConstraintViolationWithTemplate(
                    "Email list contains empty or null values"
                ).addConstraintViolation();
                return false;
            }
            
            if (!EMAIL_PATTERN.matcher(email.trim()).matches()) {
                context.disableDefaultConstraintViolation();
                context.buildConstraintViolationWithTemplate(
                    String.format("Invalid email format: %s", email)
                ).addConstraintViolation();
                return false;
            }
        }
        
        return true;
    }
}
