import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { AuditService } from '../../core/services/audit.service';
import { AuthService } from '../../core/services/auth.service';
import { AuditSession } from '../../core/models/audit.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective],
  template: `
    <div style="min-height: 100vh; background-color: #0b0f19; color: #f3f4f6; font-family: 'Inter', system-ui, -apple-system, sans-serif; padding: 32px 24px;">
      <div style="max-width: 1100px; margin: 0 auto;">
        
        <!-- Header Bar -->
        <header style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 24px; border-bottom: 1px solid #1f2937; margin-bottom: 32px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: linear-gradient(135deg, #6366f1, #a855f7); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: white;">V</div>
            <div>
              <h1 style="margin: 0; font-size: 22px; font-weight: 700; tracking-tight: -0.025em; color: #ffffff;">VibeCheck Platform</h1>
              <p style="margin: 2px 0 0 0; font-size: 13px; color: #9ca3af;">Code Audit & Agentic Compliance Hub</p>
            </div>
          </div>
          <button (click)="onLogout()" style="padding: 10px 18px; background: #1f2937; color: #e5e7eb; border: 1px solid #374151; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='#374151'" onmouseout="this.style.background='#1f2937'">
            Logout
          </button>
        </header>

        <!-- Dynamic Overview Cards & Chart Gauge -->
        <div style="display: grid; grid-template-columns: 280px 1fr; gap: 24px; margin-bottom: 32px;">
          <!-- Gauge Container -->
          <div style="background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
            <div style="width: 180px; height: 180px; position: relative;">
              <canvas baseChart
                [data]="doughnutChartData"
                [type]="doughnutChartType"
                [options]="doughnutChartOptions">
              </canvas>
            </div>
            <div style="text-align: center; margin-top: 16px;">
              <span style="font-size: 32px; font-weight: 800; color: #6366f1;">{{ averageScore }}%</span>
              <p style="margin: 4px 0 0 0; font-size: 13px; color: #9ca3af; font-weight: 500;">Average Audit Compliance</p>
            </div>
          </div>

          <!-- Quick Metrics Banner -->
          <div style="display: grid; grid-template-rows: 1fr 1fr; gap: 16px;">
            <div style="background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; display: flex; align-items: center; justify-content: space-between;">
              <div>
                <p style="margin: 0; font-size: 13px; color: #9ca3af; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Total Audits Run</p>
                <h2 style="margin: 6px 0 0 0; font-size: 36px; font-weight: 800; color: #ffffff;">{{ audits.length }}</h2>
              </div>
              <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); padding: 16px; border-radius: 12px;">
                <svg width="28" height="28" fill="none" stroke="#818cf8" viewBox="0 0 24 24" stroke-width="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
            </div>

            <div style="background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; display: flex; align-items: center; justify-content: space-between;">
              <div>
                <p style="margin: 0; font-size: 13px; color: #9ca3af; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Pipeline Status</p>
                <h2 style="margin: 6px 0 0 0; font-size: 20px; font-weight: 700; color: #10b981;">Agentic Pipeline Active</h2>
              </div>
              <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 16px; border-radius: 12px;">
                <svg width="28" height="28" fill="none" stroke="#34d399" viewBox="0 0 24 24" stroke-width="2"><path d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Trigger Form Container -->
        <div style="background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 28px; margin-bottom: 32px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
          <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #ffffff;">Launch Code Audit Session</h3>
            <p style="margin: 4px 0 0 0; font-size: 14px; color: #9ca3af;">Specify your code source and custom SCOPE.md compliance validation rules.</p>
          </div>

          <form (ngSubmit)="triggerAudit()">
            <div style="margin-bottom: 20px;">
              <label style="display: block; font-size: 13px; font-weight: 600; color: #d1d5db; margin-bottom: 8px;">Repository Target / Local Path</label>
              <input type="text" [(ngModel)]="repoSource" name="repoSource" placeholder="e.g., sample_app or https://github.com/user/repo.git" required 
                style="width: 100%; padding: 12px 16px; background: #0b0f19; border: 1px solid #374151; border-radius: 8px; color: #ffffff; font-size: 14px; box-sizing: border-box; outline: none;" />
            </div>

            <div style="margin-bottom: 24px;">
              <label style="display: block; font-size: 13px; font-weight: 600; color: #d1d5db; margin-bottom: 8px;">SCOPE.md Ruleset Definition</label>
              <textarea [(ngModel)]="scopeContent" name="scopeContent" rows="4" 
                style="width: 100%; padding: 12px 16px; background: #0b0f19; border: 1px solid #374151; border-radius: 8px; color: #a7f3d0; font-family: monospace; font-size: 13px; box-sizing: border-box; outline: none; line-height: 1.5;"></textarea>
            </div>

            <button type="submit" [disabled]="loading" 
              style="padding: 12px 28px; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: opacity 0.2s; display: inline-flex; align-items: center; gap: 8px;">
              <span *ngIf="loading" style="width: 16px; height: 16px; border: 2px solid #ffffff; border-top-color: transparent; border-radius: 50%; display: inline-block; animation: spin 1s linear infinite;"></span>
              {{ loading ? 'Executing Analysis Pipeline...' : 'Run Audit Session' }}
            </button>
          </form>
        </div>

        <!-- History Table Section -->
        <div style="background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 28px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="margin: 0; font-size: 18px; font-weight: 700; color: #ffffff;">Audit Execution Log</h2>
            <button (click)="loadAudits()" style="padding: 8px 14px; background: #1f2937; color: #9ca3af; border: 1px solid #374151; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer;" onmouseover="this.style.color='#ffffff'" onmouseout="this.style.color='#9ca3af'">
              Refresh Output
            </button>
          </div>

          <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: separate; border-spacing: 0; text-align: left;">
              <thead>
                <tr style="background: #1f2937; color: #9ca3af; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em;">
                  <th style="padding: 14px 16px; border-top-left-radius: 8px;">ID</th>
                  <th style="padding: 14px 16px;">Target Repository</th>
                  <th style="padding: 14px 16px;">Status</th>
                  <th style="padding: 14px 16px;">Compliance Score</th>
                  <th style="padding: 14px 16px; border-top-right-radius: 8px;">Timestamp</th>
                </tr>
              </thead>
              <tbody style="font-size: 14px; color: #e5e7eb;">
                <tr *ngFor="let audit of audits" style="border-bottom: 1px solid #1f2937; transition: background 0.2s;" onmouseover="this.style.background='#1f2937'" onmouseout="this.style.background='transparent'">
                  <td style="padding: 16px; border-bottom: 1px solid #1f2937; font-family: monospace; color: #818cf8;">#{{ audit.id }}</td>
                  <td style="padding: 16px; border-bottom: 1px solid #1f2937; font-weight: 500;">{{ audit.repo_source }}</td>
                  <td style="padding: 16px; border-bottom: 1px solid #1f2937;">
                    <span [style.background]="audit.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)'"
                          [style.color]="audit.status === 'COMPLETED' ? '#34d399' : '#f87171'"
                          [style.border]="audit.status === 'COMPLETED' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)'"
                          style="padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; letter-spacing: 0.025em; display: inline-block;">
                      {{ audit.status }}
                    </span>
                  </td>
                  <td style="padding: 16px; border-bottom: 1px solid #1f2937; font-weight: 700;" [style.color]="audit.compliance_score >= 80 ? '#34d399' : '#fbbf24'">
                    {{ audit.compliance_score }}%
                  </td>
                  <td style="padding: 16px; border-bottom: 1px solid #1f2937; color: #9ca3af; font-size: 13px;">{{ audit.created_at | date:'medium' }}</td>
                </tr>
                <tr *ngIf="audits.length === 0">
                  <td colspan="5" style="padding: 32px; text-align: center; color: #6b7280; font-size: 14px; border-bottom: 1px solid #1f2937;">
                    No audit sessions recorded. Trigger a new analysis above!
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  audits: AuditSession[] = [];
  repoSource = 'sample_app';
  scopeContent = '# Scope Rules\n- Must pass pytest\n- Must pass ruff linter';
  loading = false;
  averageScore = 0;

  public doughnutChartType: ChartType = 'doughnut';
  public doughnutChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    }
  };
  public doughnutChartData: ChartData<'doughnut'> = {
    labels: ['Compliant', 'Non-Compliant'],
    datasets: [
      {
        data: [0, 100],
        backgroundColor: ['#6366f1', '#1f2937'],
        borderWidth: 0
      }
    ]
  };

  constructor(
    private auditService: AuditService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadAudits();
  }

  loadAudits(): void {
    this.auditService.getAudits().subscribe({
      next: (data) => {
        this.audits = data;
        this.updateChart();
      },
      error: (err) => console.error('Failed to load audits:', err)
    });
  }

  updateChart(): void {
    if (this.audits.length === 0) {
      this.averageScore = 0;
      this.doughnutChartData.datasets[0].data = [0, 100];
    } else {
      const total = this.audits.reduce((acc, curr) => acc + curr.compliance_score, 0);
      this.averageScore = Math.round(total / this.audits.length);
      this.doughnutChartData.datasets[0].data = [this.averageScore, 100 - this.averageScore];
    }
    this.doughnutChartData = { ...this.doughnutChartData };
  }

  triggerAudit(): void {
    if (!this.repoSource) return;
    this.loading = true;
    this.auditService.createAudit({
      repo_source: this.repoSource,
      scope_content: this.scopeContent
    }).subscribe({
      next: () => {
        this.loading = false;
        this.loadAudits();
      },
      error: (err) => {
        this.loading = false;
        console.error('Failed to start audit:', err);
      }
    });
  }

  onLogout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}