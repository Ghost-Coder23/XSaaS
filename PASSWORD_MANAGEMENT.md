# EduCore Password Management & User Onboarding Documentation

This document explains the secure onboarding process and password management workflow for all user types (Teachers, Parents, Students, and Admins).

## 1. Secure Onboarding Flow

### **New User Invitations**
When a new user is added to a school (via the Admin panel or registration views):
1.  **Account Creation**: A standard Django `User` object is created with a strong, random password.
2.  **Membership Link**: A `SchoolUser` record is created linking that user to the specific school with a designated role (e.g., 'teacher', 'student').
3.  **Welcome Email**: The system sends an automated welcome email containing:
    *   A personalized greeting.
    *   The name of the school they were added to.
    *   A secure **Set Password** link (generated via Django's token system).

### **Existing User Invitations**
If a person already has an EduCore account (e.g., they are a parent at one school and are being added as a teacher at another):
1.  **Conflict Resolution**: The system detects the existing email and skips account creation.
2.  **Membership Link**: A new `SchoolUser` record is created for the new school.
3.  **Notification Email**: The user receives an email informing them they've been added to a new school. Since they already have a password, no reset link is sent; instead, they are directed to the login page.

## 2. Password Recovery (Forgot Password)

### **Workflow**
1.  **Request**: User clicks "Forgot Password?" on the login screen and enters their email.
2.  **Subdomain Awareness**: The system automatically detects the school subdomain (e.g., `greenwood.educore.com`) and generates a recovery link that points back to that specific subdomain.
3.  **Secure Token**: A unique, one-time-use token is generated and emailed to the user.
4.  **Completion**: Upon clicking the link, the user is prompted to enter a new password. Once submitted, the old password and the token are invalidated.

## 3. Role-Based Access Control (RBAC) & Passwords
*   **Admins**: Can trigger invitations but **cannot see or set** user passwords directly. This is a security feature.
*   **Parents**: Can register themselves by providing their child's admission number. The system verifies the link and either creates a new account or links an existing one.
*   **Students**: Are onboarded by school admins. Their accounts are created with their registered email.

## 4. Technical Details
*   **Utility**: All onboarding logic is centralized in `core.utils.send_welcome_email`.
*   **Security**: Links are generated using `request.build_absolute_uri()` to ensure they respect HTTPS and correct subdomains.
*   **UI**: All password-related screens use a modern "Glassmorphism" design that is mobile-friendly and consistent across the platform.

---
*Note: For security reasons, the random temporary passwords generated during creation are never displayed or emailed. Users must always use the secure token link to set their own password.*
