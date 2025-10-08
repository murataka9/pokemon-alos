"""
ビジュアライゼーション: Matplotlibを使ったリアルタイム表示
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
from typing import Dict, List
import numpy as np
import japanize_matplotlib


class PokemonVisualizer:
    """ポケモンシミュレーションのビジュアライザー"""
    
    def __init__(self, simulation_engine, update_interval: int = 500):
        """
        Args:
            simulation_engine: シミュレーションエンジン
            update_interval: 更新間隔（ミリ秒）
        """
        self.engine = simulation_engine
        self.update_interval = update_interval
        
        # フィギュアとサブプロットの作成
        self.fig = plt.figure(figsize=(14, 8))
        
        # メインの2Dマップ
        self.ax_map = plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=2)
        self.ax_map.set_xlim(0, 10)
        self.ax_map.set_ylim(0, 10)
        self.ax_map.set_aspect('equal')
        self.ax_map.set_title('ポケモンシミュレーション - 2Dマップ', fontsize=14, fontweight='bold')
        self.ax_map.set_xlabel('X座標')
        self.ax_map.set_ylabel('Y座標')
        self.ax_map.grid(True, alpha=0.3)
        
        # ステータス表示
        self.ax_status = plt.subplot2grid((2, 3), (0, 2))
        self.ax_status.axis('off')
        self.ax_status.set_title('ステータス', fontsize=12, fontweight='bold')
        
        # ログ表示
        self.ax_log = plt.subplot2grid((2, 3), (1, 2))
        self.ax_log.axis('off')
        self.ax_log.set_title('イベントログ', fontsize=12, fontweight='bold')
        
        # ポケモンの散布図プロット
        self.scatter = None
        self.pokemon_texts = {}
        self.status_text = None
        self.log_text = None
        
        # アイテムの散布図プロット
        self.item_scatter = None
        self.item_texts = {}
        
        # 凡例用のパッチ
        self.legend_patches = []
        
        plt.tight_layout()
    
    def init_plot(self):
        """プロットの初期化"""
        state = self.engine.get_simulation_state()
        
        # ポケモンの初期位置と色
        positions = []
        colors = []
        sizes = []
        
        for key, pokemon_data in state['pokemons'].items():
            pos = pokemon_data['position']
            positions.append(pos)
            colors.append(pokemon_data['color'])
            sizes.append(300)
        
        if positions:
            positions_array = np.array(positions)
            self.scatter = self.ax_map.scatter(
                positions_array[:, 0],
                positions_array[:, 1],
                c=colors,
                s=sizes,
                alpha=0.7,
                edgecolors='black',
                linewidths=2
            )
            
            # ポケモン名のテキスト
            for i, (key, pokemon_data) in enumerate(state['pokemons'].items()):
                pos = pokemon_data['position']
                text = self.ax_map.text(
                    pos[0], pos[1] + 0.3,
                    pokemon_data['name'],
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
                )
                self.pokemon_texts[key] = text
        
        # アイテムの初期化
        self._init_items(state)
        
        # 凡例を作成
        self._update_legend(state)
        
        # ステータスを初期化
        self._update_status_text(state)
        
        # ログを初期化
        self._update_log_text()
        
        return self.scatter,
    
    def _update_legend(self, state: Dict):
        """凡例を更新"""
        self.legend_patches = []
        
        # ポケモンごとの色を凡例に表示
        pokemon_colors = {
            "pikachu": ((1.0, 0.9, 0.0), "ピカチュウ"),
            "meowth": ((0.7, 0.7, 0.7), "ニャース"),
            "sprigatito": ((0.2, 0.8, 0.3), "ニャオハ")
        }
        
        for key, (color, name) in pokemon_colors.items():
            if key in state['pokemons']:
                patch = mpatches.Patch(color=color, label=name)
                self.legend_patches.append(patch)
        
        self.ax_map.legend(
            handles=self.legend_patches,
            loc='upper left',
            fontsize=9,
            title='ポケモン'
        )
    
    def _init_items(self, state: Dict):
        """アイテムの初期化"""
        items_data = state.get('items', [])
        if items_data:
            positions = [item['position'] for item in items_data]
            colors = [item['color'] for item in items_data]
            
            if positions:
                positions_array = np.array(positions)
                self.item_scatter = self.ax_map.scatter(
                    positions_array[:, 0],
                    positions_array[:, 1],
                    c=colors,
                    s=100,
                    alpha=0.8,
                    marker='s',  # 四角形
                    edgecolors='gold',
                    linewidths=1.5
                )
    
    def update_plot(self, frame):
        """プロットを更新"""
        # シミュレーションを1ステップ進める
        self.engine.step()
        state = self.engine.get_simulation_state()
        
        # ポケモンの位置と色を更新
        positions = []
        colors = []
        
        for key, pokemon_data in state['pokemons'].items():
            pos = pokemon_data['position']
            positions.append(pos)
            colors.append(pokemon_data['color'])
            
            # テキストの位置を更新
            if key in self.pokemon_texts:
                self.pokemon_texts[key].set_position((pos[0], pos[1] + 0.3))
        
        if positions:
            positions_array = np.array(positions)
            self.scatter.set_offsets(positions_array)
            self.scatter.set_facecolors(colors)
        
        # アイテムを更新
        self._update_items(state)
        
        # ステータステキストを更新
        self._update_status_text(state)
        
        # ログテキストを更新
        self._update_log_text()
        
        return self.scatter,
    
    def _update_items(self, state: Dict):
        """アイテムの表示を更新"""
        items_data = state.get('items', [])
        
        # 既存のアイテムscatterを削除
        if self.item_scatter is not None:
            self.item_scatter.remove()
            self.item_scatter = None
        
        # アイテムテキストを削除
        for text in self.item_texts.values():
            text.remove()
        self.item_texts.clear()
        
        # 新しいアイテムを描画
        if items_data:
            positions = [item['position'] for item in items_data]
            colors = [item['color'] for item in items_data]
            
            if positions:
                positions_array = np.array(positions)
                self.item_scatter = self.ax_map.scatter(
                    positions_array[:, 0],
                    positions_array[:, 1],
                    c=colors,
                    s=100,
                    alpha=0.8,
                    marker='s',  # 四角形
                    edgecolors='gold',
                    linewidths=1.5
                )
                
                # アイテムの絵文字を表示
                for i, item in enumerate(items_data):
                    pos = item['position']
                    text = self.ax_map.text(
                        pos[0], pos[1],
                        item['emoji'],
                        ha='center',
                        va='center',
                        fontsize=12
                    )
                    self.item_texts[i] = text
    
    def _update_status_text(self, state: Dict):
        """ステータスをビジュアルに表示"""
        if self.status_text:
            self.status_text.remove()
        
        # ステータスエリアをクリア
        self.ax_status.clear()
        self.ax_status.axis('off')
        self.ax_status.set_xlim(0, 1)
        self.ax_status.set_ylim(0, 1)
        self.ax_status.set_title('ステータス', fontsize=12, fontweight='bold', pad=10)
        
        # Step数を表示（左上）
        self.ax_status.text(
            0.05, 0.98,
            f"Step: {state['step']}",
            transform=self.ax_status.transAxes,
            ha='left',
            va='top',
            fontsize=9,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.5, edgecolor='blue', linewidth=1)
        )
        
        # ポケモンごとのステータスカードを描画
        y_start = 0.88
        card_height = 0.28
        y_position = y_start
        
        # 各ポケモンのステータス
        for idx, (key, pokemon_data) in enumerate(state['pokemons'].items()):
            name = pokemon_data['name']
            hp = pokemon_data['hp']
            energy = pokemon_data['energy']
            mood = pokemon_data['mood']
            color = pokemon_data['color']
            abilities = pokemon_data.get('abilities', [])
            inventory = pokemon_data.get('inventory', [])
            
            # カードの背景（ポケモンの色で）
            card_y = y_position - card_height
            card_rect = plt.Rectangle(
                (0.02, card_y),
                0.96,
                card_height,
                transform=self.ax_status.transAxes,
                facecolor=color,
                alpha=0.15,
                edgecolor=color,
                linewidth=2,
                zorder=0
            )
            self.ax_status.add_patch(card_rect)
            
            # ポケモン名（左上）
            self.ax_status.text(
                0.08, y_position - 0.02,
                name,
                transform=self.ax_status.transAxes,
                ha='left',
                va='top',
                fontsize=10,
                fontweight='bold',
                color='black',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.8, edgecolor='black', linewidth=1.5)
            )
            
            # HPとEnergyを円形プログレスで表示（左側）
            circle_y = y_position - 0.14
            
            # HP円形プログレス
            self._draw_circular_progress(
                self.ax_status, 0.15, circle_y, hp, "HP",
                (1.0, 0.2, 0.2), (0.2, 0.8, 0.2)
            )
            
            # Energy円形プログレス
            self._draw_circular_progress(
                self.ax_status, 0.32, circle_y, energy, "EN",
                (1.0, 0.6, 0.0), (0.3, 0.6, 1.0)
            )
            
            # 気分（右上）
            mood_emoji = self._get_mood_emoji(mood)
            self.ax_status.text(
                0.92, y_position - 0.02,
                f"{mood_emoji}",
                transform=self.ax_status.transAxes,
                ha='right',
                va='top',
                fontsize=16
            )
            self.ax_status.text(
                0.92, y_position - 0.06,
                mood,
                transform=self.ax_status.transAxes,
                ha='right',
                va='top',
                fontsize=7
            )
            
            # 技と持ち物（右側に表示）
            info_y = y_position - 0.1
            
            # 技（最大4個表示）
            if abilities:
                self.ax_status.text(
                    0.52, info_y,
                    f"⚡ 技 ({len(abilities)})",
                    transform=self.ax_status.transAxes,
                    ha='left',
                    fontsize=7,
                    fontweight='bold',
                    color='darkblue'
                )
                
                display_abilities = abilities[:4]
                for i, ability in enumerate(display_abilities):
                    self.ax_status.text(
                        0.54, info_y - 0.025 * (i + 1),
                        f"• {ability[:6]}",  # 最大6文字
                        transform=self.ax_status.transAxes,
                        ha='left',
                        fontsize=6
                    )
            
            # 持ち物（右側下部）
            bag_y = card_y + 0.02
            if inventory:
                self.ax_status.text(
                    0.52, bag_y,
                    f"🎒 {len(inventory)}/3",
                    transform=self.ax_status.transAxes,
                    ha='left',
                    fontsize=7,
                    fontweight='bold',
                    color='darkgreen'
                )
                
                # アイテムをアイコンで表示
                for i, item in enumerate(inventory):
                    self.ax_status.text(
                        0.68 + i * 0.1, bag_y,
                        item['emoji'],
                        transform=self.ax_status.transAxes,
                        ha='center',
                        fontsize=12,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='gold', linewidth=1)
                    )
            
            # 関係性（カード下部にミニバーで表示）
            if pokemon_data['relationships']:
                rel_y = card_y + 0.01
                rel_x_start = 0.08
                
                for i, (other_key, relationship) in enumerate(pokemon_data['relationships'].items()):
                    other_name = self.engine.pokemons[other_key].name
                    rel_x = rel_x_start + i * 0.13
                    
                    # 関係性バー
                    bar_width = 0.1
                    bar_height = 0.008
                    
                    # 背景
                    bg_rect = plt.Rectangle(
                        (rel_x, rel_y),
                        bar_width,
                        bar_height,
                        transform=self.ax_status.transAxes,
                        facecolor='lightgray',
                        edgecolor='gray',
                        linewidth=0.5
                    )
                    self.ax_status.add_patch(bg_rect)
                    
                    # 関係性の値に応じた色とサイズ
                    rel_normalized = (relationship + 100) / 200.0  # 0-1に正規化
                    if relationship > 30:
                        bar_color = (0.2, 0.8, 0.2)  # 緑
                    elif relationship < -30:
                        bar_color = (0.8, 0.2, 0.2)  # 赤
                    else:
                        bar_color = (0.8, 0.8, 0.2)  # 黄
                    
                    fill_width = bar_width * rel_normalized
                    fill_rect = plt.Rectangle(
                        (rel_x, rel_y),
                        fill_width,
                        bar_height,
                        transform=self.ax_status.transAxes,
                        facecolor=bar_color,
                        edgecolor='none'
                    )
                    self.ax_status.add_patch(fill_rect)
                    
                    # 相手の名前（1文字）
                    self.ax_status.text(
                        rel_x + bar_width / 2, rel_y - 0.01,
                        other_name[0],
                        transform=self.ax_status.transAxes,
                        ha='center',
                        va='top',
                        fontsize=6,
                        fontweight='bold'
                    )
            
            y_position -= card_height + 0.02  # 次のカードへ
    
    def _draw_circular_progress(self, ax, x, y, value, label, low_color, high_color):
        """円形プログレスバーを描画"""
        radius = 0.055
        
        # 背景円
        bg_circle = plt.Circle(
            (x, y),
            radius,
            transform=ax.transAxes,
            facecolor='lightgray',
            edgecolor='gray',
            linewidth=1.5,
            zorder=1
        )
        ax.add_patch(bg_circle)
        
        # プログレス円（パイチャート風）
        if value > 0:
            # 色の決定
            if value < 30:
                color = low_color
            elif value < 70:
                t = (value - 30) / 40.0
                color = tuple(low_color[i] * (1-t) + high_color[i] * t for i in range(3))
            else:
                color = high_color
            
            # 円弧を描画（上から時計回り）
            theta = np.linspace(np.pi/2, np.pi/2 - 2*np.pi*(value/100), 100)
            x_arc = x + radius * 0.85 * np.cos(theta)
            y_arc = y + radius * 0.85 * np.sin(theta)
            
            # 塗りつぶし
            wedge = mpatches.Wedge(
                (x, y), radius * 0.85, 90 - 360*(value/100), 90,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor='none',
                zorder=2
            )
            ax.add_patch(wedge)
        
        # 中央に白い円
        center_circle = plt.Circle(
            (x, y),
            radius * 0.6,
            transform=ax.transAxes,
            facecolor='white',
            edgecolor='none',
            zorder=3
        )
        ax.add_patch(center_circle)
        
        # 数値表示
        ax.text(
            x, y,
            f"{value:.0f}",
            transform=ax.transAxes,
            ha='center',
            va='center',
            fontsize=9,
            fontweight='bold',
            zorder=4
        )
        
        # ラベル
        ax.text(
            x, y - radius - 0.01,
            label,
            transform=ax.transAxes,
            ha='center',
            va='top',
            fontsize=7,
            fontweight='bold'
        )
    
    def _draw_status_bar(self, ax, x, y, value, label, low_color, high_color):
        """ステータスバーを描画"""
        bar_width = 0.6
        bar_height = 0.03
        
        # 背景バー（グレー）
        ax.add_patch(plt.Rectangle(
            (x, y - bar_height/2), bar_width, bar_height,
            transform=ax.transAxes,
            facecolor='lightgray',
            edgecolor='black',
            linewidth=0.5
        ))
        
        # 値のバー（色は値に応じて変化）
        if value > 0:
            fill_width = bar_width * (value / 100.0)
            # 値が低いと赤系、高いと緑/青系
            if value < 30:
                bar_color = low_color
            elif value < 70:
                # 中間色を補間
                t = (value - 30) / 40.0
                bar_color = tuple(low_color[i] * (1-t) + high_color[i] * t for i in range(3))
            else:
                bar_color = high_color
            
            ax.add_patch(plt.Rectangle(
                (x, y - bar_height/2), fill_width, bar_height,
                transform=ax.transAxes,
                facecolor=bar_color,
                edgecolor='none'
            ))
        
        # ラベルと値
        ax.text(
            x - 0.02, y,
            label,
            transform=ax.transAxes,
            ha='right',
            va='center',
            fontsize=7,
            fontweight='bold'
        )
        
        ax.text(
            x + bar_width + 0.02, y,
            f"{value:.0f}",
            transform=ax.transAxes,
            ha='left',
            va='center',
            fontsize=7,
            family='monospace'
        )
    
    def _get_mood_emoji(self, mood: str) -> str:
        """気分に対応する絵文字を返す"""
        mood_emojis = {
            "normal": "😐",
            "happy": "😊",
            "angry": "😠",
            "tired": "😴",
            "excited": "✨"
        }
        return mood_emojis.get(mood, "😐")
    
    def _update_log_text(self):
        """ログテキストを更新"""
        if self.log_text:
            self.log_text.remove()
        
        recent_logs = self.engine.get_recent_logs(n=15)
        log_text = '\n'.join(recent_logs[-15:])  # 最新15件
        
        # 日本語と絵文字に対応したフォント設定
        self.log_text = self.ax_log.text(
            0.05, 0.95,
            log_text,
            transform=self.ax_log.transAxes,
            verticalalignment='top',
            fontsize=7,
            wrap=True,
            fontfamily='sans-serif'  # monospaceから変更
        )
    
    def run(self):
        """アニメーションを実行"""
        anim = FuncAnimation(
            self.fig,
            self.update_plot,
            init_func=self.init_plot,
            interval=self.update_interval,
            blit=False,
            cache_frame_data=False
        )
        
        plt.show()
        return anim


class SimplePokemonVisualizer:
    """シンプルなポケモンビジュアライザー（ライフゲーム風）"""
    
    def __init__(self, simulation_engine, grid_size: int = 50, update_interval: int = 500):
        """
        Args:
            simulation_engine: シミュレーションエンジン
            grid_size: グリッドのサイズ
            update_interval: 更新間隔（ミリ秒）
        """
        self.engine = simulation_engine
        self.grid_size = grid_size
        self.update_interval = update_interval
        
        # グリッドの初期化
        self.grid = np.zeros((grid_size, grid_size, 3))
        
        # フィギュアとサブプロットの作成
        self.fig, (self.ax_grid, self.ax_log) = plt.subplots(1, 2, figsize=(14, 6))
        
        # グリッド表示
        self.im = self.ax_grid.imshow(self.grid, interpolation='nearest', vmin=0, vmax=1)
        self.ax_grid.set_title('ポケモンシミュレーション（グリッドビュー）', fontsize=14, fontweight='bold')
        self.ax_grid.axis('off')
        
        # ログ表示
        self.ax_log.axis('off')
        self.ax_log.set_title('イベントログ', fontsize=12, fontweight='bold')
        self.log_text = None
        
        plt.tight_layout()
    
    def init_plot(self):
        """プロットの初期化"""
        self._update_grid()
        return self.im,
    
    def _update_grid(self):
        """グリッドを更新"""
        # グリッドをリセット
        self.grid = np.zeros((self.grid_size, self.grid_size, 3))
        
        state = self.engine.get_simulation_state()
        
        for key, pokemon_data in state['pokemons'].items():
            pos = pokemon_data['position']
            color = pokemon_data['color']
            
            # 位置をグリッド座標に変換
            x = int(pos[0] / 10.0 * self.grid_size)
            y = int(pos[1] / 10.0 * self.grid_size)
            
            # 境界チェック
            x = max(0, min(self.grid_size - 1, x))
            y = max(0, min(self.grid_size - 1, y))
            
            # グリッドに色を設定（3x3の領域）
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        self.grid[ny, nx] = color
        
        self.im.set_data(self.grid)
    
    def update_plot(self, frame):
        """プロットを更新"""
        # シミュレーションを1ステップ進める
        self.engine.step()
        
        # グリッドを更新
        self._update_grid()
        
        # ログを更新
        self._update_log_text()
        
        return self.im,
    
    def _update_log_text(self):
        """ログテキストを更新"""
        if self.log_text:
            self.log_text.remove()
        
        recent_logs = self.engine.get_recent_logs(n=30)
        log_text = '\n'.join(recent_logs[-30:])
        
        # 日本語と絵文字に対応したフォント設定
        self.log_text = self.ax_log.text(
            0.05, 0.95,
            log_text,
            transform=self.ax_log.transAxes,
            verticalalignment='top',
            fontsize=7,
            fontfamily='sans-serif'  # monospaceから変更
        )
    
    def run(self):
        """アニメーションを実行"""
        anim = FuncAnimation(
            self.fig,
            self.update_plot,
            init_func=self.init_plot,
            interval=self.update_interval,
            blit=False,
            cache_frame_data=False
        )
        
        plt.show()
        return anim

