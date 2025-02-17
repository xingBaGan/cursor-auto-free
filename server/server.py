from flask import Flask, jsonify, request
from cursor_signup_service import CursorSignupService
from logger import logging
import json
import random
import string
import os
from datetime import datetime

app = Flask(__name__)

class CardManager:
    def __init__(self):
        self.cards_file = "cards.json"
        self.load_cards()

    def load_cards(self):
        """加载卡密数据"""
        if os.path.exists(self.cards_file):
            with open(self.cards_file, 'r', encoding='utf-8') as f:
                self.cards = json.load(f)
        else:
            self.cards = {}
            self.save_cards()

    def save_cards(self):
        """保存卡密数据"""
        with open(self.cards_file, 'w', encoding='utf-8') as f:
            json.dump(self.cards, f, ensure_ascii=False, indent=2)

    def generate_card(self):
        """生成新的卡密"""
        chars = string.ascii_uppercase + string.digits
        while True:
            card = 'CURSOR-' + ''.join(random.choices(chars, k=12))
            if card not in self.cards:
                self.cards[card] = {
                    'accounts': [],
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'active'
                }
                self.save_cards()
                return card

    def get_available_card(self):
        """获取可用的卡密"""
        # 查找未满5个账号的卡密
        for card, info in self.cards.items():
            if len(info['accounts']) < 5 and info['status'] == 'active':
                return card
        # 如果没有可用卡密，生成新的
        return self.generate_card()

    def add_account_to_card(self, card, account_info):
        """将账号添加到卡密"""
        if card not in self.cards:
            return False
        
        if len(self.cards[card]['accounts']) >= 5:
            return False
            
        self.cards[card]['accounts'].append(account_info)
        self.save_cards()
        return True

    def get_card_info(self, card):
        """获取卡密信息"""
        return self.cards.get(card)

card_manager = CardManager()

@app.route('/signup', methods=['POST'])
def signup():
    try:
        # 获取可用卡密
        card = card_manager.get_available_card()
        
        # 注册新账号
        signup_service = CursorSignupService()
        result = signup_service.sign_up_account()
        
        if result['success']:
            # 将账号信息添加到卡密
            account_info = {
                'email': result['email'],
                'password': result['password'],
                'token': result['token'],
                'usage_limit': result['usage_limit'],
                'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            card_manager.add_account_to_card(card, account_info)
            
            # 获取卡密当前状态
            card_info = card_manager.get_card_info(card)
            accounts_count = len(card_info['accounts'])
            
            return jsonify({
                'success': True,
                'data': {
                    'card': card,
                    'account': account_info,
                    'card_info': {
                        'total_accounts': accounts_count,
                        'remaining_slots': 5 - accounts_count
                    }
                },
                'message': 'Account created and assigned to card successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 400
            
    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/cards/<card>', methods=['GET'])
def get_card(card):
    """获取卡密详细信息"""
    card_info = card_manager.get_card_info(card)
    if card_info:
        return jsonify({
            'success': True,
            'data': {
                'card': card,
                'info': card_info
            }
        }), 200
    return jsonify({
        'success': False,
        'message': 'Card not found'
    }), 404

def print_cards_status():
    """打印所有卡密状态"""
    print("\n=== Cursor 卡密系统状态 ===")
    print("时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)
    
    for card, info in card_manager.cards.items():
        accounts_count = len(info['accounts'])
        print(f"\n卡密: {card}")
        print(f"创建时间: {info['created_at']}")
        print(f"状态: {info['status']}")
        print(f"已绑定账号数: {accounts_count}/5")
        
        if accounts_count > 0:
            print("\n绑定的账号:")
            for i, account in enumerate(info['accounts'], 1):
                print(f"\n账号 {i}:")
                print(f"  邮箱: {account['email']}")
                print(f"  密码: {account['password']}")
                print(f"  额度: {account['usage_limit']}")
                print(f"  添加时间: {account['added_at']}")
        
        print("-" * 50)
    
    print("\n=== 统计信息 ===")
    total_cards = len(card_manager.cards)
    total_accounts = sum(len(info['accounts']) for info in card_manager.cards.values())
    print(f"总卡密数: {total_cards}")
    print(f"总账号数: {total_accounts}")
    print("=" * 50 + "\n")

if __name__ == '__main__':
    # 启动时打印当前状态
    print_cards_status()
    app.run(host='0.0.0.0', port=5000) 