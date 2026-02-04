#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-add user profile fields to forms
"""
import re

print("🚀 Adding user profile fields...\n")

# 1. Add hometown to User model
print("1. Updating User model...")
with open('app/models/user.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'hometown' not in content:
    # Add hometown after facebook_link
    content = content.replace(
        "facebook_link = db.Column(db.String(255), nullable=True)  # Facebook/Social media\r\n    join_date",
        "facebook_link = db.Column(db.String(255), nullable=True)  # Facebook/Social media\r\n    hometown = db.Column(db.String(100), nullable=True)  # Quê quán\r\n    join_date"
    )
    with open('app/models/user.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✓ Added hometown field to User model")
else:
    print("   ℹ️ hometown already exists")

# 2. Add fields to admin user form  
print("\n2. Updating admin user form...")
with open('app/templates/admin/user_form.html','r', encoding='utf-8') as f:
    lines = f.readlines()

# Find insertion point (before role selection)
insert_at = None
for i, line in enumerate(lines):
    if 'id="role"' in line and 'name="role"' in line:
        # Go back to find the start of this row div
        for j in range(i-1, max(0, i-10), -1):
            if '<div class="row">' in lines[j]:
                insert_at = j
                break
        break

if insert_at and 'date_of_birth' not in ''.join(lines):
    new_fields = '''                        <!-- Additional Profile Fields -->
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="date_of_birth" class="form-label">Ngày sinh</label>
                                <input type="date" class="form-control" id="date_of_birth" name="date_of_birth"
                                    value="{{ user.date_of_birth.strftime('%Y-%m-%d') if user and user.date_of_birth else '' }}">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="phone_number" class="form-label">Số điện thoại</label>
                                <input type="tel" class="form-control" id="phone_number" name="phone_number"
                                    value="{{ user.phone_number or '' }}" placeholder="+84 ...">
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="facebook_link" class="form-label">Facebook</label>
                                <input type="url" class="form-control" id="facebook_link" name="facebook_link"
                                    value="{{ user.facebook_link or '' }}" placeholder="https://facebook.com/...">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="hometown" class="form-label">Quê quán</label>
                                <input type="text" class="form-control" id="hometown" name="hometown"
                                    value="{{ user.hometown or '' }}" placeholder="Hà Nội, TP HCM...">
                            </div>
                        </div>

'''
    lines.insert(insert_at, new_fields)
    with open('app/templates/admin/user_form.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("   ✓ Added fields to admin user form")
else:
    print("   ℹ️ Fields already exist or couldn't find insertion point")

print("\n✅ Done! Next steps:")
print("   1. Run: flask db migrate -m 'Add hometown field'")
print("   2. Run: flask db upgrade")
print("   3. Update member profile form similarly")
print("   4. Update backend routes to handle new fields")
