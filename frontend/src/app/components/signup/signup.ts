import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div style="min-height: 100vh; background-color: #0b0f19; display: flex; align-items: center; justify-content: center; font-family: 'Inter', system-ui, -apple-system, sans-serif; padding: 20px;">
      <div style="width: 100%; max-width: 420px; background: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 40px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);">
        
        <div style="text-align: center; margin-bottom: 32px;">
          <div style="background: linear-gradient(135deg, #a855f7, #ec4899); width: 48px; height: 48px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-weight: 800; font-size: 24px; color: white; margin-bottom: 16px;">V</div>
          <h2 style="margin: 0; font-size: 24px; font-weight: 700; color: #ffffff;">Create an Account</h2>
          <p style="margin: 8px 0 0 0; font-size: 14px; color: #9ca3af;">Get started with VibeCheck code auditing</p>
        </div>

        <div *ngIf="errorMessage" style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; text-align: center;">
          {{ errorMessage }}
        </div>

        <form (ngSubmit)="onSignup()">
          <div style="margin-bottom: 20px;">
            <label style="display: block; font-size: 13px; font-weight: 600; color: #d1d5db; margin-bottom: 8px;">Email Address</label>
            <input type="email" [(ngModel)]="email" name="email" placeholder="dev@vibecheck.io" required 
              style="width: 100%; padding: 12px 16px; background: #0b0f19; border: 1px solid #374151; border-radius: 8px; color: #ffffff; font-size: 14px; box-sizing: border-box; outline: none;" />
          </div>

          <div style="margin-bottom: 24px;">
            <label style="display: block; font-size: 13px; font-weight: 600; color: #d1d5db; margin-bottom: 8px;">Password</label>
            <input type="password" [(ngModel)]="password" name="password" placeholder="••••••••" required 
              style="width: 100%; padding: 12px 16px; background: #0b0f19; border: 1px solid #374151; border-radius: 8px; color: #ffffff; font-size: 14px; box-sizing: border-box; outline: none;" />
          </div>

          <button type="submit" 
            style="width: 100%; padding: 12px; background: linear-gradient(135deg, #a855f7, #ec4899); color: white; border: none; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: opacity 0.2s;">
            Create Account
          </button>
        </form>

        <p style="margin-top: 24px; text-align: center; font-size: 14px; color: #9ca3af;">
          Already have an account? <a routerLink="/login" style="color: #c084fc; text-decoration: none; font-weight: 600;">Sign in</a>
        </p>
      </div>
    </div>
  `
})
export class SignupComponent {
  email = '';
  password = '';
  errorMessage = '';

  constructor(private authService: AuthService, private router: Router) {}

  onSignup(): void {
    this.authService.signup(this.email, this.password).subscribe({
      next: () => this.router.navigate(['/login']),
      error: (err) => this.errorMessage = err.error?.detail || 'Signup failed'
    });
  }
}