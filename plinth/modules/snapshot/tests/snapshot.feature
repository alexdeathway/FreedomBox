# SPDX-License-Identifier: AGPL-3.0-or-later

@system @snapshot
Feature: Storage Snapshots
  Run storage snapshots application - Snapper.

Background:
  Given I'm a logged in user
  And the snapshot application is installed
  And the filesystem supports snapshots

Scenario: Create a snapshot
  Given the list of snapshots is empty
  When I manually create a snapshot
  Then there should be 1 more snapshots in the list

Scenario: Configure snapshots
  Given snapshots are configured with free space 30, timeline snapshots disabled, software snapshots disabled, hourly limit 10, daily limit 3, weekly limit 2, monthly limit 2, yearly limit 0
  When I configure snapshots with free space 20, timeline snapshots enabled, software snapshots enabled, hourly limit 3, daily limit 2, weekly limit 1, monthly limit 1, yearly limit 1
  Then snapshots should be configured with free space 20, timeline snapshots enabled, software snapshots enabled, hourly limit 3, daily limit 2, weekly limit 1, monthly limit 1, yearly limit 1

@backups
Scenario: Backup and restore snapshot
  When I configure snapshots with free space 30, timeline snapshots disabled, software snapshots disabled, hourly limit 10, daily limit 3, weekly limit 2, monthly limit 2, yearly limit 0
  And I create a backup of the snapshot app data with name test_storage_snapshots
  And I configure snapshots with free space 20, timeline snapshots enabled, software snapshots enabled, hourly limit 3, daily limit 2, weekly limit 1, monthly limit 1, yearly limit 1
  And I restore the snapshot app data backup with name test_storage_snapshots
  Then snapshots should be configured with free space 30, timeline snapshots disabled, software snapshots disabled, hourly limit 10, daily limit 3, weekly limit 2, monthly limit 2, yearly limit 0
